#!/usr/bin/env python3
"""Draw naturalization-steps.png from steps.json, so the picture and the page never disagree.
Needs Pillow. Run it by hand after changing steps.json:  python3 make_steps_picture.py"""
import json
from PIL import Image, ImageDraw, ImageFont

S = json.load(open("steps.json", encoding="utf-8"))
W, PAD = 1080, 64
REG, BOLD = "/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
def font(size, bold=False): return ImageFont.truetype(BOLD if bold else REG, size)
INK, MUTED, LINE, BG, CARD, BRAND = "#1c2430", "#5b6573", "#e3dfd6", "#f6f4ef", "#ffffff", "#14365c"
PHASE = ["#14365c", "#1f6f8b", "#9a5b12", "#1f7a4d"]          # one colour per phase
SOFT = ["#e7eef6", "#e3f1f5", "#fbefd5", "#e3f3ea"]

def wrap(d, text, f, width):
    out, line = [], ""
    for word in text.split():
        t = (line + " " + word).strip()
        if d.textlength(t, font=f) <= width: line = t
        else: out.append(line); line = word
    return out + [line]

def draw(d, measure_only=False):
    y = 0
    d.rectangle([0, 0, W, 300], fill=BRAND)
    d.text((PAD, 70), S["title"], font=font(62, True), fill="#ffffff")
    d.text((PAD, 160), S["sub"], font=font(34), fill="#d6e2f0")
    d.text((PAD, 222), "Checked " + S["checked"], font=font(26), fill="#a9bdd4")
    y = 300 + 40
    X, R = PAD + 36, 36                                        # centre and radius of the numbered circles
    TX = X + R + 28                                            # where the text starts
    TW = W - PAD - TX
    for pi, ph in enumerate(S["phases"]):
        d.rounded_rectangle([PAD, y, PAD + 40 + d.textlength(ph["name"].upper(), font=font(26, True)), y + 50], 25, fill=PHASE[pi])
        d.text((PAD + 20, y + 11), ph["name"].upper(), font=font(26, True), fill="#ffffff")
        y += 50 + 26
        for si, st in enumerate(ph["steps"]):
            top = y
            title = wrap(d, st["t"], font(36, True), TW)
            desc = wrap(d, st["d"], font(30), TW)
            yy = y + 4
            for t in title: d.text((TX, yy), t, font=font(36, True), fill=INK); yy += 46
            yy += 4
            for t in desc: d.text((TX, yy), t, font=font(30), fill=MUTED); yy += 40
            if st["k"]:
                yy += 10
                kw = d.textlength(st["k"], font=font(26, True))
                d.rounded_rectangle([TX, yy, TX + kw + 36, yy + 46], 12, fill=SOFT[pi])
                d.text((TX + 18, yy + 9), st["k"], font=font(26, True), fill=PHASE[pi])
                yy += 46
            bottom = yy + 34
            last = pi == len(S["phases"]) - 1 and si == len(ph["steps"]) - 1
            if not last: d.line([X, top + R * 2, X, bottom + (76 if si == len(ph["steps"]) - 1 else 0)], fill=LINE, width=5)
            d.ellipse([X - R, top, X + R, top + R * 2], fill=PHASE[pi])
            n = str(st["n"]); nf = font(34, True)
            d.text((X - d.textlength(n, font=nf) / 2, top + 17), n, font=nf, fill="#ffffff")
            y = bottom
        y += 10
    y += 10
    d.line([PAD, y, W - PAD, y], fill=LINE, width=2); y += 28
    for t in wrap(d, S["source"], font(26), W - 2 * PAD): d.text((PAD, y), t, font=font(26), fill=MUTED); y += 36
    d.text((PAD, y + 6), S["url"], font=font(28, True), fill=BRAND); y += 60
    return y + 30

probe = ImageDraw.Draw(Image.new("RGB", (W, 100), BG))
H = draw(ImageDraw.Draw(Image.new("RGB", (W, 6000), BG)))
im = Image.new("RGB", (W, H), BG)
draw(ImageDraw.Draw(im))
im.save("naturalization-steps.png", optimize=True)
print("naturalization-steps.png", im.size)
