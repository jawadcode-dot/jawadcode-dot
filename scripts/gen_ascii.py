import numpy as np
import cv2
from PIL import Image

import sys

SRC = "assets/favicon.png"
THEME = sys.argv[1] if len(sys.argv) > 1 else "dark"
OUT_SVG = f"assets/ascii-portrait-{THEME}.svg"

RAMP = " .`:-=+*cs#%@"
COLS = 90
CHAR_W = 5.0            # px, design width per character
CELL_ASPECT = 0.48       # matches guide: rows = cols*(h/w)*CELL_ASPECT
LINE_H = CHAR_W / CELL_ASPECT
PAD = 18
FONT_SIZE = LINE_H * 0.92
FILL = "#d8d2ea" if THEME == "dark" else "#2e1f52"
STAGGER = 0.07           # seconds between row starts
ROW_DUR = 0.5

im = Image.open(SRC).convert("RGBA")
bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
flat = Image.alpha_composite(bg, im).convert("RGB")
arr = np.array(flat)

alpha = np.array(im)[:, :, 3]
ys, xs = np.where(alpha > 10)
y0, y1 = ys.min(), ys.max()
x0, x1 = xs.min(), xs.max()
pad_px = int(0.03 * max(x1 - x0, y1 - y0))
y0 = max(0, y0 - pad_px)
x0 = max(0, x0 - pad_px)
y1 = min(arr.shape[0] - 1, y1 + pad_px)
x1 = min(arr.shape[1] - 1, x1 + pad_px)
crop = arr[y0:y1, x0:x1]

gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
gray = cv2.bilateralFilter(gray, d=9, sigmaColor=60, sigmaSpace=60)

lo, hi = np.percentile(gray, 2), np.percentile(gray, 98)
stretched = np.clip((gray.astype(np.float32) - lo) / max(hi - lo, 1) * 255.0, 0, 255)

norm = stretched / 255.0
curved = np.power(norm, 1.15) * 255.0
curved = curved.astype(np.uint8)

h, w = curved.shape
rows = max(1, round(COLS * (h / w) * CELL_ASPECT))
small = cv2.resize(curved, (COLS, rows), interpolation=cv2.INTER_AREA)

levels = len(RAMP) - 1
idx = np.round((255 - small.astype(np.float32)) / 255.0 * levels).astype(int)
idx = np.clip(idx, 0, levels)

lines = ["".join(RAMP[v] for v in row) for row in idx]

width = PAD * 2 + COLS * CHAR_W
height = PAD * 2 + rows * LINE_H

text_rows = []
for i, line in enumerate(lines):
    esc = (
        line.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    y = PAD + (i + 0.85) * LINE_H
    begin = round(i * STAGGER, 3)
    row_w = COLS * CHAR_W
    text_rows.append(f'''  <clipPath id="cp{i}">
    <rect x="{PAD}" y="{y - LINE_H}" width="0" height="{LINE_H * 1.2:.2f}">
      <animate attributeName="width" from="0" to="{row_w}" begin="{begin}s" dur="{ROW_DUR}s" fill="freeze"/>
    </rect>
  </clipPath>''')

texts = []
for i, line in enumerate(lines):
    esc = (
        line.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    y = PAD + (i + 0.85) * LINE_H
    row_w = COLS * CHAR_W
    texts.append(
        f'  <text x="{PAD}" y="{y:.2f}" clip-path="url(#cp{i})" '
        f'textLength="{row_w}" lengthAdjust="spacingAndGlyphs">{esc}</text>'
    )

svg = f'''<svg viewBox="0 0 {width:.1f} {height:.1f}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="ascii portrait">
  <defs>
{chr(10).join(text_rows)}
  </defs>
  <style>
    text {{
      font-family: 'JetBrains Mono', 'Fira Code', Consolas, 'Courier New', monospace;
      font-size: {FONT_SIZE:.2f}px;
      fill: {FILL};
      white-space: pre;
    }}
  </style>
{chr(10).join(texts)}
</svg>
'''

with open(OUT_SVG, "w", encoding="utf-8") as f:
    f.write(svg)

print("rows", rows, "cols", COLS, "size", f"{width:.0f}x{height:.0f}")
print(lines[len(lines)//2])
