"""Render the build/verify flow diagram for the README (1280x460).

    python .github/assets/make_diagram.py

Same look as the banner. Kept as an image (not mermaid) so it renders the same
everywhere, including GitHub's mobile app and link previews.
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 2
W, H = 1280 * S, 460 * S
FONT_DIR = os.environ.get("FONT_DIR", "C:/Windows/Fonts/")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build-flow.png")

def P(v):
    return v * S

def font(name, size):
    assert size >= 20, f"{name} at {size}px is too small"
    return ImageFont.truetype(FONT_DIR + name, int(size * S))

rng = np.random.default_rng(9)
BG = (22, 23, 28)
CARD = (240, 235, 224)
INK = (34, 32, 30)
SUB = (88, 82, 74)
GREEN = (78, 176, 112)
RED = (214, 72, 84)
CREAM = (244, 236, 222)
problems = []

img = Image.new("RGB", (W, H), BG)
arr = np.asarray(img).astype(np.float32)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
arr += np.array([30, 22, 14], np.float32) * np.exp(-(((xx - W / 2) / (W * 0.6)) ** 2 + ((yy - H / 2) / (H * 0.9)) ** 2))[..., None]
arr += rng.normal(0, 3.5, (H, W, 1)).astype(np.float32)
img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
d = ImageDraw.Draw(img)

title_f = font("segoeuib.ttf", 30)
d.text((P(48), P(34)), "How every image is built and verified", font=title_f, fill=CREAM)

STEPS = [
    ("1  Release tag", "RELEASE.2025-10-15T17-29-55Z", None),
    ("2  Commit check", "tag must match the pinned commit", "else the build stops"),
    ("3  go build", "CGO off, amd64 + arm64", None),
    ("4  Image", "alpine, non-root, minio + mc", None),
    ("5  Smoke test", "health, version, lock, retention", "else nothing is published"),
    ("6  Publish", "ghcr.io with provenance + SBOM", None),
]
cols, gap_x, gap_y = 3, P(40), P(64)
cw = (W - P(96) - gap_x * (cols - 1)) / cols
ch = P(124)
top = P(104)
hf, sf, ff = font("segoeuib.ttf", 26), font("segoeui.ttf", 21), font("segoeuib.ttf", 21)
cards = []
for i, (head, line1, fail) in enumerate(STEPS):
    r, c = divmod(i, cols)
    x0 = P(48) + c * (cw + gap_x)
    y0 = top + r * (ch + gap_y)
    box = (x0, y0, x0 + cw, y0 + ch)
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((box[0] + P(4), box[1] + P(6), box[2] + P(4), box[3] + P(6)), radius=P(12), fill=(0, 0, 0, 120))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(P(6))))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, radius=P(12), fill=CARD)
    accent = (52, 120, 200) if i == len(STEPS) - 1 else (RED if fail else GREEN)
    d.rounded_rectangle((box[0], box[1], box[0] + P(8), box[3]), radius=P(4), fill=accent)
    rows = [(head, hf, INK, P(18)), (line1, sf, SUB, P(56))]
    if fail:
        rows.append((fail, ff, RED, P(86)))
    for txt, f, col, y in rows:
        b = d.textbbox((box[0] + P(26), box[1] + y), txt, font=f)
        if b[2] > box[2] - P(14) or b[3] > box[3] - P(6):
            problems.append(f"'{txt}' overflows its card")
        d.text((box[0] + P(26), box[1] + y), txt, font=f, fill=col)
    cards.append(box)

def arrow_h(a, b):
    y = (a[1] + a[3]) / 2
    x0, x1 = a[2] + P(6), b[0] - P(6)
    d.line([(x0, y), (x1 - P(10), y)], fill=GREEN, width=int(P(4)))
    d.polygon([(x1, y), (x1 - P(13), y - P(9)), (x1 - P(13), y + P(9))], fill=GREEN)

for i in range(len(cards) - 1):
    if (i + 1) % cols:
        arrow_h(cards[i], cards[i + 1])
# end of row 1 to start of row 2: down, across, down
a, b = cards[cols - 1], cards[cols]
ax, bx = (a[0] + a[2]) / 2, (b[0] + b[2]) / 2
my = a[3] + gap_y / 2
d.line([(ax, a[3] + P(6)), (ax, my), (bx, my), (bx, b[1] - P(14))], fill=GREEN, width=int(P(4)), joint="curve")
d.polygon([(bx, b[1] - P(4)), (bx - P(9), b[1] - P(17)), (bx + P(9), b[1] - P(17))], fill=GREEN)

if problems:
    raise SystemExit("REFUSING TO WRITE:\n" + "\n".join(problems))
img.convert("RGB").resize((1280, 460), Image.LANCZOS).save(OUT, optimize=True)
print("saved", OUT)
