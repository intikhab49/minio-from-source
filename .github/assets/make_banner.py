"""Render the README banner / GitHub social preview (1280x640).

    python .github/assets/make_banner.py

Pillow + numpy only. Windows fonts (Segoe UI, Cascadia Mono); on another OS,
point FONT_DIR at equivalents. Same visual language as the launch post: warm
dark painted ground, one realistic kraft box, paper label with a rubber stamp.
No MinIO logo (trademark).
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 2
W, H = 1280 * S, 640 * S
FONT_DIR = os.environ.get("FONT_DIR", "C:/Windows/Fonts/")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "banner.png")
MIN_PT = 22

def P(v):
    return v * S

def font(name, size):
    assert size >= MIN_PT, f"{name} at {size}px is below the {MIN_PT}px floor"
    return ImageFont.truetype(FONT_DIR + name, int(size * S))

random.seed(4)
rng = np.random.default_rng(4)
CREAM = (244, 236, 222)
DIM = (198, 200, 210)
GREEN = (46, 140, 84)
CHIP_BG = (44, 42, 46)
problems = []

def inside(name, box, pad=36):
    if box[0] < P(pad) or box[1] < P(pad) or box[2] > W - P(pad) or box[3] > H - P(pad):
        problems.append(f"{name} escapes the safe area {tuple(round(v / S) for v in box)}")

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

# ---------- painted warm-dark ground + warm key light behind the box
bg = Image.new("RGB", (W, H), (18, 19, 24))
d = ImageDraw.Draw(bg)
pal = [(20, 21, 27), (23, 23, 29), (19, 20, 25), (25, 24, 30), (21, 22, 27)]
for _ in range(16000):
    x, y = random.uniform(-40, W + 40), random.uniform(-40, H + 40)
    a = -0.55 + random.gauss(0, 0.22)
    length = random.uniform(P(16), P(58))
    c = random.choice(pal)
    j = random.randint(-3, 3)
    d.line([(x, y), (x + length * math.cos(a), y + length * math.sin(a))],
           fill=tuple(max(0, v + j) for v in c), width=random.randint(int(P(4)), int(P(11))))
bg = bg.filter(ImageFilter.GaussianBlur(P(0.9)))
arr = np.asarray(bg).astype(np.float32)
pool = np.exp(-(((xx - W * 0.80) / (W * 0.30)) ** 2 + ((yy - H * 0.52) / (H * 0.55)) ** 2))
arr += np.array([58, 42, 26], np.float32) * pool[..., None]

def poly_mask(pts, blur=0):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([(P(x), P(y)) for x, y in pts], fill=255)
    if blur:
        m = m.filter(ImageFilter.GaussianBlur(P(blur)))
    return np.asarray(m).astype(np.float32)[..., None] / 255

# ---------- kraft box on the right, light from the top left
FL, FR, BR, BL = (868, 236), (1196, 236), (1196, 512), (868, 512)
DX, DY = 52, -40
TOP = [FL, (FL[0] + DX, FL[1] + DY), (FR[0] + DX, FR[1] + DY), FR]
SIDE = [FR, (FR[0] + DX, FR[1] + DY), (BR[0] + DX, BR[1] + DY), BR]
FRONT = [FL, FR, BR, BL]
shadow = poly_mask([(BL[0] + 6, BL[1] - 4), (BR[0] + DX + 40, BR[1] + DY + 18),
                    (BR[0] + DX + 70, BR[1] + 22), (BL[0] + 36, BL[1] + 22)], blur=16)
contact = poly_mask([(BL[0] - 3, BL[1] - 3), (BR[0] + 3, BR[1] - 3), (BR[0] + DX, BR[1] + DY),
                     (BR[0] + 6, BR[1] + 7), (BL[0] + 3, BL[1] + 7)], blur=5)
arr *= np.clip(1 - 0.72 * shadow - 0.62 * contact, 0.12, 1)

fib = Image.fromarray(np.clip(128 + rng.normal(0, 60, (H // 4, W // 4)), 0, 255).astype(np.uint8))
fib = np.asarray(fib.resize((W, H), Image.BILINEAR)).astype(np.float32) / 128 - 1
streak = Image.fromarray(np.clip(128 + rng.normal(0, 70, (H // 2, W // 16)), 0, 255).astype(np.uint8))
streak = np.asarray(streak.resize((W, H), Image.BICUBIC)).astype(np.float32) / 128 - 1
kraft = 10 * fib + 9 * streak + 5 * rng.normal(0, 1, (H, W)).astype(np.float32)

def face(pts, base, shade):
    global arr
    m = poly_mask(pts)
    col = np.array(base, np.float32)[None, None, :] + kraft[..., None] * np.array([1.0, 0.86, 0.66])
    arr = arr * (1 - m) + col * shade[..., None] * m

face(FRONT, (178, 134, 88), 1.04 - 0.16 * np.clip((yy - P(236)) / P(276), 0, 1) ** 1.6)
face(TOP, (204, 160, 110), np.ones((H, W), np.float32))
face(SIDE, (128, 96, 66), 0.96 - 0.10 * np.clip((yy - P(196)) / P(316), 0, 1))

over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(over)
def line(p, q, col, w):
    od.line([(P(p[0]), P(p[1])), (P(q[0]), P(q[1]))], fill=col, width=int(P(w)))
def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
a0, a1 = lerp(TOP[0], TOP[1], 0.36), lerp(TOP[0], TOP[1], 0.64)
b0, b1 = lerp(TOP[3], TOP[2], 0.36), lerp(TOP[3], TOP[2], 0.64)
od.polygon([(P(x), P(y)) for x, y in [a0, a1, b1, b0]], fill=(226, 190, 132, 185))
od.polygon([(P(x), P(y)) for x, y in [b0, b1, (b1[0], b1[1] + 80), (b0[0], b0[1] + 80)]], fill=(176, 140, 94, 175))
line(FL, FR, (238, 204, 156, 170), 1.6)
line(FR, BR, (78, 56, 36, 210), 2.0)
line(BL, BR, (58, 42, 28, 220), 2.0)
line(SIDE[1], SIDE[2], (60, 44, 30, 200), 1.6)
over = over.filter(ImageFilter.GaussianBlur(P(0.4)))
oa = np.asarray(over).astype(np.float32)
arr = arr * (1 - oa[..., 3:] / 255) + oa[..., :3] * (oa[..., 3:] / 255)

img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")

# ---------- paper label on the box with a green PASS stamp
lw, lh = P(280), P(194)
paper = np.full((lh, lw, 3), (241, 237, 227), np.float32) + rng.normal(0, 3.2, (lh, lw, 1))
lab = Image.fromarray(np.clip(paper, 0, 255).astype(np.uint8)).convert("RGBA")
ld = ImageDraw.Draw(lab)
f_lab, f_mono = font("segoeuib.ttf", 30), font("CascadiaMono.ttf", 22)
ld.text((P(18), P(14)), "built from source", font=f_lab, fill=(34, 32, 30))
ld.text((P(18), P(58)), "RELEASE.2025-10-15", font=f_mono, fill=(78, 74, 68))
ld.text((P(18), P(86)), "amd64 + arm64", font=f_mono, fill=(78, 74, 68))
if ld.textbbox((P(18), P(14)), "built from source", font=f_lab)[2] > lw - P(10):
    problems.append("label title overflows")
f_stamp = font("bahnschrift.ttf", 34)
sb = ld.textbbox((0, 0), "PASS", font=f_stamp)
sm = Image.new("L", (sb[2] - sb[0] + P(34), sb[3] - sb[1] + P(28)), 0)
sd = ImageDraw.Draw(sm)
sd.rounded_rectangle([P(4), P(4), sm.width - P(4), sm.height - P(4)], radius=P(6), outline=255, width=int(P(4)))
sd.text(((sm.width - (sb[2] - sb[0])) / 2 - sb[0], (sm.height - (sb[3] - sb[1])) / 2 - sb[1]), "PASS", font=f_stamp, fill=255)
sm = sm.rotate(-9, resample=Image.BICUBIC, expand=True)
coarse = Image.fromarray(np.clip(128 + rng.normal(0, 70, (sm.height // 18 + 1, sm.width // 18 + 1)), 0, 255).astype(np.uint8))
coarse = np.asarray(coarse.resize(sm.size, Image.BICUBIC)).astype(np.float32) / 255
ink = np.asarray(sm).astype(np.float32) / 255 * np.clip(0.62 + 0.42 * coarse, 0, 1) * 0.9
sx, sy = lw - sm.width - P(8), lh - sm.height - P(6)
# the stamp sits below the text, never on it
text_bottom = ld.textbbox((P(18), P(86)), "amd64 + arm64", font=f_mono)[3]
if sy + P(6) < text_bottom:
    problems.append("PASS stamp overlaps the label text")
la = np.asarray(lab).astype(np.float32).copy()
reg = la[sy:sy + sm.height, sx:sx + sm.width, :3]
la[sy:sy + sm.height, sx:sx + sm.width, :3] = reg * (1 - ink[..., None]) + (reg * np.array(GREEN, np.float32) / 235) * ink[..., None]
lab = Image.fromarray(np.clip(la, 0, 255).astype(np.uint8)).rotate(-2, resample=Image.BICUBIC, expand=True)
lx, ly = P(896), P(286)
shadow_l = Image.new("RGBA", lab.size, (0, 0, 0, 0))
shadow_l.putalpha(lab.getchannel("A").point(lambda v: int(v * 0.42)))
img.alpha_composite(shadow_l.filter(ImageFilter.GaussianBlur(P(5))), (lx + P(5), ly + P(7)))
img.alpha_composite(lab, (lx, ly))
if lx + lab.width > P(FR[0] - 6) or ly + lab.height > P(BL[1] - 6):
    problems.append("label leaves the box front")

# ---------- type, left column
d = ImageDraw.Draw(img)
X = P(72)
f_title = font("segoeuib.ttf", 74)
t = d.textbbox((X, P(92)), "minio-from-source", font=f_title)
d.text((X, P(92)), "minio-from-source", font=f_title, fill=CREAM)
inside("title", t)
if t[2] > P(FL[0] - 30):
    problems.append("title runs into the box")
f_sub = font("segoeuisl.ttf", 32)
sub_y = t[3] + P(22)
for i, s in enumerate(["MinIO server + mc, built from the public", "source at pinned, commit-verified releases."]):
    b = d.textbbox((X, sub_y + i * P(44)), s, font=f_sub)
    d.text((X, sub_y + i * P(44)), s, font=f_sub, fill=DIM)
    inside("subtitle", b)
    if b[2] > P(FL[0] - 30):
        problems.append("subtitle runs into the box")

f_chip = font("segoeuisl.ttf", 24)
cx, cy = X, sub_y + P(44) * 2 + P(34)
for chip in ["multi-arch", "smoke-tested", "provenance + SBOM", "mc included"]:
    b = d.textbbox((0, 0), chip, font=f_chip)
    w_ = b[2] - b[0] + P(32)
    if cx + w_ > P(FL[0] - 30):
        cx, cy = X, cy + P(52)
    d.rounded_rectangle([cx, cy, cx + w_, cy + P(42)], radius=P(21), fill=CHIP_BG, outline=(86, 82, 86), width=int(P(1.5)))
    d.text((cx + P(16), cy + P(21)), chip, font=f_chip, fill=CREAM, anchor="lm")
    cx += w_ + P(12)

f_code = font("CascadiaMono.ttf", 24)
code = "docker pull ghcr.io/intikhab49/minio-from-source"
code_y = cy + P(74)
cb = d.textbbox((X + P(22), code_y + P(16)), code, font=f_code)
d.rounded_rectangle([X, code_y, cb[2] + P(22), cb[3] + P(16)], radius=P(10), fill=(12, 13, 17), outline=(70, 70, 78), width=int(P(1.5)))
d.text((X + P(22), code_y + P(16)), code, font=f_code, fill=(150, 214, 160))
inside("code", (X, code_y, cb[2] + P(22), cb[3] + P(16)))
if cb[2] + P(22) > P(FL[0] - 20):
    problems.append("code box runs into the box")

f_small = font("segoeui.ttf", 22)
note = "unofficial · not affiliated with MinIO, Inc."
nb = d.textbbox((X, H - P(58)), note, font=f_small)
d.text((X, H - P(58)), note, font=f_small, fill=(150, 150, 160))
inside("note", nb, pad=24)

# ---------- vignette + grain, then write
arr = np.asarray(img.convert("RGB")).astype(np.float32)
v = np.hypot((xx - W / 2) / W, (yy - H / 2) / H)
arr *= (1 - 0.34 * np.clip(v * 1.6 - 0.25, 0, 1) ** 1.4)[..., None]
arr += rng.normal(0, 4.0, (H, W, 1)).astype(np.float32)
if problems:
    raise SystemExit("REFUSING TO WRITE:\n" + "\n".join(problems))
Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).resize((1280, 640), Image.LANCZOS).save(OUT, optimize=True)
print("saved", OUT)
