"""Procedural prop textures (PIL) for the ₹ Short. All props are fictional/stylised."""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "assets", "fonts")
OUT = os.path.join(HERE, "tex")

INK = (34, 38, 46)
SAFFRON = (240, 140, 30)


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


DEVA_B = "NotoSansDevanagari-Bold.ttf"
DEVA = "NotoSansDevanagari-Regular.ttf"
INTER_B = "Inter-Bold.otf"
INTER_XB = "Inter-ExtraBold.otf"
INTER_SB = "Inter-SemiBold.otf"
INTER = "Inter-Regular.otf"


def center_text(d, xy, text, f, fill, anchor="mm", **kw):
    d.text(xy, text, font=f, fill=fill, anchor=anchor, **kw)


def fake_lines(d, x0, y0, x1, y1, gap=26, h=10, color=(150, 150, 150), seed=1):
    rnd = random.Random(seed)
    y = y0
    while y < y1:
        w = (x1 - x0) * rnd.uniform(0.7, 1.0)
        d.rounded_rectangle([x0, y, x0 + w, y + h], radius=h // 2, fill=color)
        y += gap


def note():
    W, H = 2000, 900
    im = Image.new("RGB", (W, H), (205, 214, 190))
    d = ImageDraw.Draw(im)
    # soft gradient + guilloche
    for x in range(W):
        t = x / W
        c = (int(196 + 20 * t), int(208 + 10 * t), int(178 + 14 * t))
        d.line([(x, 0), (x, H)], fill=c)
    for k in range(18):
        pts = [(x, H / 2 + math.sin(x / (55 + k * 3) + k) * (160 + k * 9)) for x in range(0, W, 6)]
        d.line(pts, fill=(170, 186, 150), width=2)
    d.rectangle([24, 24, W - 24, H - 24], outline=(120, 140, 105), width=10)
    d.rectangle([50, 50, W - 50, H - 50], outline=(150, 168, 128), width=3)
    # medallion (abstract lotus instead of a portrait)
    cx, cy = 620, 450
    for r in range(260, 40, -22):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(130, 150, 115), width=3)
    for i in range(12):
        a = i * math.pi / 6
        d.ellipse([cx + math.cos(a) * 120 - 60, cy + math.sin(a) * 120 - 60,
                   cx + math.cos(a) * 120 + 60, cy + math.sin(a) * 120 + 60], outline=(110, 132, 98), width=4)
    center_text(d, (150, 120), "500", font(INTER_XB, 110), (88, 104, 76), anchor="lm")
    center_text(d, (1100, 140), "FIVE HUNDRED", font(INTER_B, 64), (80, 96, 70))
    fake_lines(d, 980, 260, 1400, 520, gap=40, h=12, color=(140, 158, 122), seed=4)
    # the hero symbol, bottom right, inside a ring (finger taps here)
    d.ellipse([1500, 470, 1880, 850], fill=(222, 228, 206), outline=(90, 110, 80), width=8)
    center_text(d, (1690, 655), "₹", font(DEVA_B, 300), (58, 74, 52))
    center_text(d, (1300, 760), "500", font(INTER_XB, 150), (70, 88, 62))
    return im


def newspaper():
    W, H = 1600, 2000
    im = Image.new("RGB", (W, H), (236, 230, 214))
    d = ImageDraw.Draw(im)
    center_text(d, (W / 2, 120), "DAILY SAMACHAR", font(INTER_XB, 130), INK)
    d.line([(60, 210), (W - 60, 210)], fill=INK, width=6)
    center_text(d, (W / 2, 245), "NEW DELHI  •  2009  •  ₹ 3.00", font(INTER_SB, 40), INK)
    d.line([(60, 280), (W - 60, 280)], fill=INK, width=3)
    center_text(d, (W / 2, 400), "DESIGN INDIA'S", font(INTER_XB, 150), (20, 20, 24))
    center_text(d, (W / 2, 560), "RUPEE SYMBOL", font(INTER_XB, 150), (200, 40, 40))
    center_text(d, (W / 2, 690), "Nationwide competition open to every citizen", font(INTER_SB, 52), INK)
    # picture box with a big question mark
    d.rectangle([80, 790, 900, 1500], fill=(205, 198, 182), outline=INK, width=4)
    center_text(d, (490, 1145), "?", font(INTER_XB, 520), (120, 112, 98))
    fake_lines(d, 960, 800, W - 80, 1500, gap=34, h=12, color=(120, 116, 108), seed=2)
    fake_lines(d, 80, 1560, 760, H - 80, gap=34, h=12, color=(120, 116, 108), seed=3)
    fake_lines(d, 840, 1560, W - 80, H - 80, gap=34, h=12, color=(120, 116, 108), seed=5)
    return im.filter(ImageFilter.GaussianBlur(0.6))


def design_card(kind):
    W, H = 800, 1000
    im = Image.new("RGB", (W, H), (250, 248, 242))
    d = ImageDraw.Draw(im)
    d.rectangle([14, 14, W - 14, H - 14], outline=(200, 196, 186), width=6)
    c = (W / 2, H / 2 - 40)
    if kind == 0:
        center_text(d, c, "Rs", font(INTER_XB, 340), INK)
    elif kind == 1:
        center_text(d, c, "R", font(INTER_XB, 420), INK)
        d.line([(170, 420), (630, 420)], fill=INK, width=26)
    elif kind == 2:
        d.ellipse([170, 160, 630, 620], outline=INK, width=26)
        center_text(d, (W / 2, H / 2 - 50), "र", font(DEVA_B, 320), INK)
    elif kind == 3:
        center_text(d, c, "R", font(INTER_B, 400), INK)
        d.line([(190, 330), (610, 330)], fill=INK, width=20)
        d.line([(190, 400), (610, 400)], fill=INK, width=20)
    else:
        center_text(d, c, "₹", font(DEVA_B, 520), INK)
    center_text(d, (W / 2, H - 120), f"ENTRY  #{[214, 1077, 2390, 3021, 1652][kind]}",
                font(INTER_SB, 46), (120, 116, 108))
    return im


def label(text, W=1200, H=360, bg=(200, 40, 40), fg=(255, 255, 255), f=INTER_XB, size=200):
    im = Image.new("RGB", (W, H), bg)
    center_text(ImageDraw.Draw(im), (W / 2, H / 2), text, font(f, size), fg)
    return im


def gate_sign():
    im = label("IIT GUWAHATI", 2400, 420, (245, 240, 228), (40, 52, 90), INTER_XB, 230)
    ImageDraw.Draw(im).rectangle([10, 10, 2390, 410], outline=(40, 52, 90), width=14)
    return im


def poster():
    W, H = 800, 1100
    im = Image.new("RGB", (W, H), (36, 44, 72))
    d = ImageDraw.Draw(im)
    for i in range(7):
        d.ellipse([100 + i * 30, 160 + i * 30, 700 - i * 30, 760 - i * 30],
                  outline=[(240, 140, 30), (250, 250, 250), (40, 150, 70)][i % 3], width=14)
    center_text(d, (W / 2, 900), "DESIGN", font(INTER_XB, 140), (250, 250, 250))
    center_text(d, (W / 2, 1010), "IDC  •  2009", font(INTER_SB, 50), (200, 200, 210))
    return im


def calendar():
    im = Image.new("RGB", (600, 700), (248, 246, 240))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 600, 180], fill=(200, 40, 40))
    center_text(d, (300, 90), "2009", font(INTER_XB, 120), (255, 255, 255))
    for r in range(5):
        for cidx in range(7):
            x, y = 40 + cidx * 76, 220 + r * 92
            d.rectangle([x, y, x + 60, y + 70], outline=(180, 176, 168), width=3)
    return im


def price_board():
    W, H = 1400, 1000
    im = Image.new("RGB", (W, H), (18, 22, 30))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 200], fill=(230, 60, 40))
    center_text(d, (W / 2, 100), "FUEL PRICES", font(INTER_XB, 110), (255, 255, 255))
    for i, (name, price) in enumerate([("PETROL", "₹ 102.50"), ("DIESEL", "₹ 89.20")]):
        y = 360 + i * 330
        center_text(d, (90, y), name, font(INTER_B, 100), (240, 240, 240), anchor="lm")
        center_text(d, (W - 90, y), price, font(DEVA_B, 150), (255, 190, 40), anchor="rm")
    return im


def keyboard():
    W, H = 1600, 700
    im = Image.new("RGB", (W, H), (28, 30, 36))
    d = ImageDraw.Draw(im)
    rows = ["1234567890", "QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
    k = 140
    for r, row in enumerate(rows):
        x0 = 40 + r * 50
        for i, ch in enumerate(row):
            x, y = x0 + i * (k + 12), 30 + r * (k + 22)
            hero = (r == 0 and ch == "4")
            d.rounded_rectangle([x, y, x + k, y + k], radius=20,
                                fill=(240, 140, 30) if hero else (58, 62, 72))
            center_text(d, (x + k / 2, y + k / 2 - 18), ch, font(INTER_B, 56), (235, 235, 240))
            if hero:
                center_text(d, (x + k / 2, y + k / 2 + 34), "₹", font(DEVA_B, 64), (255, 255, 255))
    return im


def price_tag():
    W, H = 900, 520
    im = Image.new("RGB", (W, H), (250, 220, 70))
    d = ImageDraw.Draw(im)
    d.ellipse([60, H / 2 - 50, 160, H / 2 + 50], fill=(60, 50, 30))
    center_text(d, (560, 200), "₹ 499", font(DEVA_B, 230), (30, 30, 30))
    center_text(d, (560, 410), "SALE  •  KURTA", font(INTER_B, 60), (60, 50, 30))
    return im


def pay_screen():
    W, H = 900, 1800
    im = Image.new("RGB", (W, H), (245, 247, 250))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 760], fill=(26, 160, 90))
    d.ellipse([W / 2 - 170, 170, W / 2 + 170, 510], fill=(255, 255, 255))
    d.line([(W / 2 - 80, 345), (W / 2 - 15, 410), (W / 2 + 95, 280)], fill=(26, 160, 90), width=34)
    center_text(d, (W / 2, 640), "Payment Successful", font(INTER_B, 70), (255, 255, 255))
    center_text(d, (W / 2, 1000), "₹ 1,250", font(DEVA_B, 220), (20, 24, 30))
    center_text(d, (W / 2, 1180), "Paid to Chai Corner", font(INTER_SB, 56), (100, 106, 116))
    fake_lines(d, 120, 1320, W - 120, 1650, gap=60, h=18, color=(205, 210, 218), seed=9)
    return im


def proof_card():
    W, H = 1000, 1250
    im = Image.new("RGB", (W, H), (252, 251, 247))
    d = ImageDraw.Draw(im)
    center_text(d, (W / 2, 520), "₹", font(DEVA_B, 760), (20, 22, 28))
    center_text(d, (W / 2, 1060), "Indian Rupee Sign  •  U+20B9", font(INTER_SB, 50), (110, 110, 110))
    return im


def sketch_paper():
    W, H = 1000, 1250
    im = Image.new("RGB", (W, H), (244, 238, 222))
    d = ImageDraw.Draw(im)
    for y in range(120, H, 60):
        d.line([(0, y), (W, y)], fill=(200, 210, 228), width=2)
    gray = (80, 80, 86)
    center_text(d, (260, 300), "र", font(DEVA, 300), gray)
    center_text(d, (500, 300), "+", font(INTER, 160), gray)
    center_text(d, (740, 300), "R", font(INTER, 260), gray)
    center_text(d, (W / 2, 820), "₹", font(DEVA, 520), (40, 40, 46))
    return im.filter(ImageFilter.GaussianBlur(1.0))


def paper_plain():
    im = Image.new("RGB", (1200, 1600), (246, 241, 228))
    d = ImageDraw.Draw(im)
    rnd = random.Random(7)
    for _ in range(4000):
        x, y = rnd.randrange(1200), rnd.randrange(1600)
        v = rnd.randint(228, 240)
        d.point((x, y), fill=(v, v - 4, v - 14))
    for y in range(140, 1600, 70):
        d.line([(0, y), (1200, y)], fill=(212, 220, 236), width=2)
    return im


def checks():
    """Light blue checked shirt fabric (tileable)."""
    W = 256
    im = Image.new("RGB", (W, W), (140, 185, 230))
    d = ImageDraw.Draw(im)
    for i in range(0, W, 64):
        d.rectangle([i, 0, i + 18, W], fill=(60, 105, 170))
        d.rectangle([0, i, W, i + 18], fill=(60, 105, 170))
    return im


ALL = {
    "note": note, "newspaper": newspaper, "gate_sign": gate_sign, "poster": poster,
    "calendar": calendar, "price_board": price_board, "keyboard": keyboard,
    "price_tag": price_tag, "pay_screen": pay_screen, "proof_card": proof_card,
    "sketch_paper": sketch_paper, "paper_plain": paper_plain, "checks": checks,
    "entries": lambda: label("ENTRIES", 1400, 420, (200, 40, 40), (255, 255, 255), INTER_XB, 240),
    "committee": lambda: label("RUPEE SYMBOL — FINAL 5", 2400, 300, (60, 40, 30), (245, 225, 180), INTER_XB, 150),
}
for _k in range(5):
    ALL[f"design{_k}"] = (lambda k=_k: design_card(k))


def build_all():
    os.makedirs(OUT, exist_ok=True)
    paths = {}
    for name, fn in ALL.items():
        p = os.path.join(OUT, name + ".png")
        if not os.path.exists(p):
            fn().save(p)
        paths[name] = p
    return paths


if __name__ == "__main__":
    print(build_all())
