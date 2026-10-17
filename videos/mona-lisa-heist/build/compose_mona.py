# Insert the real Mona Lisa (softened) into picture frames of a clip.
# usage: compose.py in.mp4 out_frames_dir mona.png config_json debug_prefix
import sys, json, cv2, numpy as np
inp, outdir, mona_path, cfg_s, dbg = sys.argv[1:6]
cfg = json.loads(cfg_s)
mode = cfg.get("mode", "full")          # full | light | nored
method = cfg.get("method", "gold")      # gold | hole | static | white
roi = cfg.get("roi")                    # [x0,y0,x1,y1]
inset = cfg.get("inset", 0.16)
vanish = cfg.get("vanish")              # frame index where the painting disappears

def order(q):
    q = np.array(q, np.float32).reshape(4, 2)
    s = q.sum(1); d = np.diff(q, axis=1).ravel()
    return np.array([q[np.argmin(s)], q[np.argmin(d)], q[np.argmax(s)], q[np.argmax(d)]], np.float32)

def gold_mask(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lo = cfg.get("gold_lo", [8, 60, 90]); hi = cfg.get("gold_hi", [35, 255, 255])
    m = cv2.inRange(hsv, tuple(lo), tuple(hi))
    kk = cfg.get("close", 5)
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((kk, kk), np.uint8))

def in_roi(m):
    if roi:
        z = np.zeros_like(m); x0, y0, x1, y1 = roi; z[y0:y1, x0:x1] = m[y0:y1, x0:x1]; return z
    return m

def det_gold(img):
    m = in_roi(gold_mask(img))
    cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = [c for c in cnts if cv2.contourArea(c) > cfg.get("min_area", 800)]
    if not cnts: return None
    c = max(cnts, key=cv2.contourArea)
    r = cv2.minAreaRect(c)
    (cx, cy), (w, h), a = r
    r2 = ((cx, cy), (w * (1 - 2 * inset), h * (1 - 2 * inset)), a)
    return order(cv2.boxPoints(r2))

def det_hole(img):
    m = in_roi(gold_mask(img))
    cnts, hier = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if hier is None: return None
    best = None
    for i, c in enumerate(cnts):
        if hier[0][i][3] == -1: continue
        a = cv2.contourArea(c); x, y, w, h = cv2.boundingRect(c)
        if a < 600 or a / (w * h) < 0.6: continue
        if best is None or a > best[0]: best = (a, c)
    if best is None: return None
    c = best[1]; peri = cv2.arcLength(c, True); q = cv2.approxPolyDP(c, 0.04 * peri, True)
    if len(q) != 4: q = cv2.boxPoints(cv2.minAreaRect(c))
    return order(q)

def det_white(img):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dark = in_roi((g < 110).astype(np.uint8) * 255)
    dark = cv2.morphologyEx(dark, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    cnts, hier = cv2.findContours(dark, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if hier is None: return None
    best = None
    for i, c in enumerate(cnts):
        if hier[0][i][3] == -1: continue        # holes inside dark line drawing
        a = cv2.contourArea(c); x, y, w, h = cv2.boundingRect(c)
        if a < 20000 or a / (w * h) < 0.85 or not (1.1 < h / w < 1.7): continue
        if best is None or a < best[0]: best = (a, c)   # innermost large rectangle
    if best is None: return None
    c = best[1]; peri = cv2.arcLength(c, True); q = cv2.approxPolyDP(c, 0.03 * peri, True)
    if len(q) != 4: q = cv2.boxPoints(cv2.minAreaRect(c))
    q = order(q); ctr = q.mean(0); return ctr + (q - ctr) * 0.97

DET = {"gold": det_gold, "hole": det_hole, "white": det_white, "static": det_hole}

cap = cv2.VideoCapture(inp); frames = []
while True:
    ok, f = cap.read()
    if not ok: break
    frames.append(f)
qs = [DET[method](f) for f in frames]
n = len(frames)
if method == "static":
    ok = [q for q in qs if q is not None]
    med = np.median(np.stack(ok), 0); qs = [med] * n
# fill gaps by nearest neighbour, then temporal smoothing
idx = [i for i, q in enumerate(qs) if q is not None]
if not idx:
    print("NO DETECTIONS"); sys.exit(1)
filled = []
for i in range(n):
    j = min(idx, key=lambda k: abs(k - i)); filled.append(np.array(qs[j], np.float32))
arr = np.stack(filled)
k = cfg.get("smooth", 5)
sm = np.stack([np.median(arr[max(0, i - k // 2): i + k // 2 + 1], 0) for i in range(n)])
sm = np.stack([sm[max(0, i - 1): i + 2].mean(0) for i in range(n)])

# softened Mona Lisa
mona = cv2.imread(mona_path)
soft = cv2.bilateralFilter(mona, 7, 40, 7)
hsv = cv2.cvtColor(soft, cv2.COLOR_BGR2HSV).astype(np.float32); hsv[..., 1] *= 0.9
soft = cv2.cvtColor(hsv.clip(0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
edges = cv2.Canny(cv2.GaussianBlur(mona, (5, 5), 0), 60, 140)
edges = cv2.dilate(edges, np.ones((2, 2), np.uint8))
soft[edges > 0] = (soft[edges > 0] * 0.55).astype(np.uint8)        # light ink lines
H, W = soft.shape[:2]
src = np.array([[0, 0], [W - 1, 0], [W - 1, H - 1], [0, H - 1]], np.float32)

for i, f in enumerate(frames):
    q = sm[i]
    if vanish is not None and i >= vanish + 3:
        cv2.imwrite(f"{outdir}/f_{i:04d}.png", f); continue
    region = None
    if cfg.get("fill"):
        # flood-fill the frame opening up to the gold border, inside the outer frame box
        ctr = q.mean(0); outer = ctr + (q - ctr) / (1 - 2 * inset) * 1.02
        box = np.zeros(f.shape[:2], np.uint8); cv2.fillConvexPoly(box, outer.astype(np.int32), 255)
        g = cv2.dilate(gold_mask(f), np.ones((3, 3), np.uint8))
        free = cv2.bitwise_and(box, cv2.bitwise_not(g))
        n_, lab = cv2.connectedComponents(free)
        cx, cy = int(ctr[0]), int(ctr[1])
        if 0 <= cy < lab.shape[0] and 0 <= cx < lab.shape[1] and lab[cy, cx] > 0:
            reg = (lab == lab[cy, cx]).astype(np.uint8) * 255
            if cv2.countNonZero(reg) > 0.5 * cv2.contourArea(q.astype(np.float32)):
                region = cv2.erode(reg, np.ones((3, 3), np.uint8))
                cnts, _ = cv2.findContours(region, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                q = order(cv2.boxPoints(cv2.minAreaRect(max(cnts, key=cv2.contourArea))))
    M = cv2.getPerspectiveTransform(src, q)
    warped = cv2.warpPerspective(soft, M, (f.shape[1], f.shape[0]))
    mask = np.zeros(f.shape[:2], np.uint8); cv2.fillConvexPoly(mask, q.astype(np.int32), 255)
    if region is not None: mask = cv2.bitwise_and(cv2.dilate(region, np.ones((3, 3), np.uint8)), mask)
    hsvf = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    if mode == "light":      # only replace blank / grey canvas, keep anything drawn on top (coat, legs)
        keep = cv2.inRange(hsvf, (0, 0, 95), (180, 45, 255))
        mask = cv2.bitwise_and(mask, keep)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    elif mode == "nored":    # keep the red X on top
        red = cv2.inRange(hsvf, (0, 90, 80), (10, 255, 255)) | cv2.inRange(hsvf, (165, 90, 80), (180, 255, 255))
        red = cv2.dilate(red, np.ones((3, 3), np.uint8))
        mask[red > 0] = 0
    alpha = cv2.GaussianBlur(mask, (3, 3), 0).astype(np.float32) / 255
    if vanish is not None and i >= vanish:
        alpha *= max(0.0, 1 - (i - vanish + 1) / 3)
    out = (f * (1 - alpha[..., None]) + warped * alpha[..., None]).astype(np.uint8)
    cv2.imwrite(f"{outdir}/f_{i:04d}.png", out)
    if i % 16 == 8:
        cv2.imwrite(f"{dbg}_{i:03d}.jpg", cv2.resize(out, (270, 480)))
print(inp, "frames", n, "detected", len(idx))
