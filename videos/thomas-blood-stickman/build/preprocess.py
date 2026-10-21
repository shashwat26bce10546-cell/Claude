# Clips 1-15 in the user's order (each clip's artwork matches its scene, so the numbering is correct).
#
# Framing: the FULL frame is kept (720x1280 -> 1080x1920, no crop). The generator's sparkle watermark
# in the bottom-right is erased in place instead: it is a fixed semi-transparent star, so its alpha
# map is measured per clip from the footage itself (the only thing that stays put while the art moves)
# and then un-composited frame by frame, with a light feather over the edge it leaves behind.
#
# Timing: the voiceover is sped up 1.22x (atempo, pitch unchanged) so the clips do not have to stretch
# much; each clip then plays ONCE, slowed at most 1.65x to cover its line. No repeats, no held frames.
import subprocess, os
import numpy as np
import cv2

os.chdir(os.path.join(os.path.dirname(__file__), ".."))

W, H = 720, 1280
X0, X1, Y0, Y1 = 540, 700, 1100, 1245      # the region the watermark lives in
SRC = 4.01
VO_SPEED = 1.22
MAX_SLOW = 1.65
FPS = 30

# scene starts (output seconds) — must match build/build.mjs
S = [0, 5.04, 8.40, 12.05, 17.50, 21.48, 25.12, 29.63, 33.44, 39.39, 42.99, 46.35, 51.43, 55.94, 59.80]
END = 64.3

subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "assets/audio/voiceover.mp3", "-af",
                f"atempo={VO_SPEED},"
                "highpass=f=70,acompressor=threshold=-22dB:ratio=2.5:attack=5:release=100:makeup=2,"
                "loudnorm=I=-15:TP=-1.5:LRA=8",
                "-ar", "48000", "-c:a", "libmp3lame", "-b:a", "192k",
                "assets/audio/voiceover-master.mp3"], check=True)


def read_gray(clip, fps=6):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"media/clips/{clip}.mp4",
                          "-vf", f"fps={fps},format=gray", "-f", "rawvideo", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)


def watermark_alpha(clip, fallback):
    """Alpha of the watermark: the one thing that holds still while the artwork pushes in."""
    als = []
    for f in read_gray(clip):
        roi = f[Y0:Y1, X0:X1]
        bg = cv2.medianBlur(roi.astype(np.uint8), 61).astype(np.float32)   # kernel >> the mark
        als.append(np.clip((roi - bg) / np.maximum(255.0 - bg, 1.0), 0, 1))
    A = np.median(np.array(als), 0)
    A[A < 0.04] = 0
    A = cv2.morphologyEx(A, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    A = cv2.GaussianBlur(A, (0, 0), 1.0)
    # keep the blob sitting where the mark is; if the artwork polluted the estimate, use the shared one
    n, lab, stats, cent = cv2.connectedComponentsWithStats((A > 0.04).astype(np.uint8))
    cy, cx = np.unravel_index(fallback.argmax(), fallback.shape)
    best, bd = None, 1e9
    for i in range(1, n):
        d = (cent[i][0] - cx) ** 2 + (cent[i][1] - cy) ** 2
        if d < bd and stats[i, cv2.CC_STAT_AREA] < 2600:
            bd, best = d, i
    if best is None or bd > 900:
        return fallback
    out = np.zeros_like(A)
    out[lab == best] = A[lab == best]
    return out


ALPHA_CACHE = "build/watermark-alpha.npy"
if os.path.exists(ALPHA_CACHE):
    ALPHAS = np.load(ALPHA_CACHE)
else:
    shared = []
    for c in (1, 2, 9, 10, 11, 12, 15):          # clips whose mark sits over flat art
        for f in read_gray(c, 4):
            roi = f[Y0:Y1, X0:X1]
            bg = cv2.medianBlur(roi.astype(np.uint8), 61).astype(np.float32)
            shared.append(np.clip((roi - bg) / np.maximum(255.0 - bg, 1.0), 0, 1))
    T = np.median(np.array(shared), 0)
    T[T < 0.04] = 0
    T = cv2.morphologyEx(T, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    T = cv2.GaussianBlur(T, (0, 0), 1.2)
    ALPHAS = np.array([watermark_alpha(c, T) for c in range(1, 16)])
    np.save(ALPHA_CACHE, ALPHAS)


def erase_watermark(frame, A, sel, mask, feather):
    roi = frame[Y0:Y1, X0:X1].astype(np.float32)
    bg = cv2.inpaint(roi.astype(np.uint8), mask, 4, cv2.INPAINT_TELEA).astype(np.float32)
    a = A[..., None]
    den = (((a * (255.0 - bg)) ** 2)[sel]).sum()
    s = float(np.clip(((roi - bg) * (a * (255.0 - bg)))[sel].sum() / max(den, 1e-6), 0, 1.6))
    Ae = np.clip(a * s, 0, 0.92)
    out = np.clip((roi - Ae * 255.0) / np.maximum(1.0 - Ae, 1e-3), 0, 255)
    out = out * (1 - feather) + cv2.GaussianBlur(out, (0, 0), 1.6) * feather
    frame[Y0:Y1, X0:X1] = out.astype(np.uint8)
    return frame


os.makedirs("media/prepped", exist_ok=True)
for i, s0 in enumerate(S):
    e = S[i + 1] if i + 1 < len(S) else END
    target = round(e - s0 + 0.65, 3)                       # scene + the composition's crossfade handles
    f = round(min(max(target / SRC, 0.70), MAX_SLOW), 4)
    A = ALPHAS[i]
    sel = A > 0.04
    mask = cv2.dilate((sel.astype(np.uint8)) * 255, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    feather = np.clip(cv2.GaussianBlur(cv2.dilate(A, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))),
                                       (0, 0), 2.5) / max(A.max(), 1e-6), 0, 1)[..., None]

    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", f"media/clips/{i+1}.mp4",
                            "-vf", "format=bgr24", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    # blended retime (motion-compensated interpolation warps flat cartoon art), then upscale
    speed = f"setpts={f}*PTS," + (f"minterpolate=fps={FPS}:mi_mode=blend" if f > 1.02 else f"fps={FPS}")
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                            "-s", f"{W}x{H}", "-r", "24", "-i", "-", "-an",
                            "-vf", speed + f",scale=1080:1920:flags=lanczos,eq=contrast=1.02:saturation=1.04,"
                                   f"trim=duration={target},setpts=PTS-STARTPTS,format=yuv420p",
                            "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                            "-movflags", "+faststart", f"media/prepped/s{i+1}.mp4"], stdin=subprocess.PIPE)
    n = 0
    while True:
        buf = dec.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        frame = np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy()
        enc.stdin.write(erase_watermark(frame, A, sel, mask, feather).tobytes())
        n += 1
    enc.stdin.close()
    dec.wait()
    enc.wait()
    print(f"slot {i+1:2d} <- clip {i+1}: {n} frames -> {target}s @x{f}", flush=True)
