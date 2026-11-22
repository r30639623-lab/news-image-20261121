#!/usr/bin/env python3
"""Render THE WORLD TODAY — Saturday 21 November 2026 front page.
Draws a 1024x1024 newspaper image with PIL only. Deterministic: no
randomness, no timestamps, no external images.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (18, 18, 18)
RED = (178, 34, 34)
DARK = (30, 30, 30)

FD = "/usr/share/fonts/truetype/dejavu/"
SERIF = FD + "DejaVuSerif.ttf"
SERIF_B = FD + "DejaVuSerif-Bold.ttf"
SANS = FD + "DejaVuSans.ttf"
SANS_B = FD + "DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, fnt, max_w, max_lines):
    """Wrap and truncate with ellipsis to max_lines."""
    lines = wrap(draw, text, fnt, max_w)[:max_lines]
    if len(wrap(draw, text, fnt, max_w)) > max_lines and lines:
        last = lines[-1]
        while last and draw.textlength(last + "…", font=fnt) > max_w:
            last = last.rsplit(" ", 1)[0] if " " in last else last[:-1]
        lines[-1] = last + "…"
    return lines


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ---------------------------------------------------------------- icons
def icon_conflict(d, x, y, w, h):
    # explosion burst, orange/red
    cx, cy = x + w // 2, y + h // 2
    pts = []
    import math
    for i in range(12):
        ang = i * math.pi / 6
        r = w // 2 - 2 if i % 2 == 0 else w // 4
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    d.polygon(pts, fill=(214, 90, 40))
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 214, 90))


def icon_justice(d, x, y, w, h):
    # scales: beam + two pans
    cx, cy = x + w // 2, y + 8
    d.line([cx, cy, cx, cy + 22], fill=(60, 60, 60), width=3)
    d.line([cx - 14, cy + 4, cx + 14, cy + 4], fill=(60, 60, 60), width=3)
    for sx in (cx - 14, cx + 14):
        d.line([sx, cy + 4, sx, cy + 14], fill=(60, 60, 60), width=2)
        d.pieslice([sx - 8, cy + 12, sx + 8, cy + 24], 0, 180, fill=(150, 110, 60))
    d.rectangle([cx - 8, cy + 26, cx + 8, cy + 30], fill=(60, 60, 60))


def icon_markets(d, x, y, w, h):
    # bar chart, red (sell-off)
    bars = [(10, 18), (24, 26), (38, 32)]
    for bx, bh in bars:
        d.rectangle([x + bx, y + h - 6 - bh, x + bx + 10, y + h - 6],
                    fill=(178, 34, 34))
    d.line([x + 6, y + h - 6, x + w - 6, y + h - 6], fill=(60, 60, 60), width=2)


def icon_climate(d, x, y, w, h):
    # sun + leaf
    cx, cy = x + 16, y + 14
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(230, 170, 40))
    for ang in range(0, 360, 45):
        import math
        r1, r2 = 10, 14
        a = math.radians(ang)
        d.line([cx + r1 * math.cos(a), cy + r1 * math.sin(a),
                cx + r2 * math.cos(a), cy + r2 * math.sin(a)],
               fill=(230, 170, 40), width=2)
    d.pieslice([x + 26, y + 16, x + 52, y + 40], 180, 360, fill=(60, 140, 70))
    d.polygon([(x + 26, y + 28), (x + 52, y + 28), (x + 39, y + 40)],
              fill=(46, 110, 55))


def icon_politics(d, x, y, w, h):
    # flag on pole
    d.rectangle([x + 14, y + 6, x + 17, y + h - 6], fill=(60, 60, 60))
    d.polygon([(x + 17, y + 6), (x + 44, y + 10), (x + 17, y + 20)],
              fill=(40, 80, 160))
    d.ellipse([x + 12, y + 4, x + 19, y + 11], fill=(230, 190, 60))


def icon_science(d, x, y, w, h):
    # atom
    cx, cy = x + w // 2, y + h // 2
    d.ellipse([cx - 14, cy - 8, cx + 14, cy + 8], outline=(40, 90, 160), width=2)
    d.ellipse([cx - 8, cy - 14, cx + 8, cy + 14], outline=(40, 90, 160), width=2)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(178, 34, 34))


def icon_tech(d, x, y, w, h):
    # chip
    d.rectangle([x + 14, y + 10, x + w - 14, y + h - 10], fill=(40, 44, 60))
    d.rectangle([x + 20, y + 16, x + w - 20, y + h - 16],
                outline=(120, 200, 220), width=2)
    for px in (18, 28, 38):
        d.line([x + px, y + 4, x + px, y + 10], fill=(120, 120, 120), width=2)
        d.line([x + px, y + h - 10, x + px, y + h - 4],
               fill=(120, 120, 120), width=2)


def icon_economy(d, x, y, w, h):
    # gold coin
    cx, cy = x + w // 2, y + h // 2
    d.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], fill=(212, 175, 55))
    d.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], outline=(150, 115, 30), width=2)
    d.text((cx, cy), "$", font=font(SANS_B, 18), fill=(120, 85, 20),
           anchor="mm")


def icon_society(d, x, y, w, h):
    # three people
    for i, px in enumerate((14, 28, 42)):
        d.ellipse([x + px - 5, y + 8, x + px + 5, y + 18], fill=(70, 110, 170))
        d.pieslice([x + px - 8, y + 20, x + px + 8, y + 38], 180, 360,
                   fill=(70, 110, 170))


def icon_health(d, x, y, w, h):
    # red cross
    cx, cy = x + w // 2, y + h // 2
    d.rectangle([cx - 5, cy - 14, cx + 5, cy + 14], fill=(200, 40, 40))
    d.rectangle([cx - 14, cy - 5, cx + 14, cy + 5], fill=(200, 40, 40))


def icon_space(d, x, y, w, h):
    # ringed planet
    cx, cy = x + w // 2, y + h // 2
    d.ellipse([cx - 18, cy - 4, cx + 18, cy + 4], outline=(150, 110, 60), width=3)
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(90, 120, 180))
    d.ellipse([cx - 15, cy - 15, cx - 9, cy - 9], fill=(255, 255, 255))


def icon_disaster(d, x, y, w, h):
    # warning triangle + wave
    cx = x + w // 2
    d.polygon([(cx, y + 6), (cx + 18, y + 30), (cx - 18, y + 30)],
              fill=(230, 180, 40))
    d.text((cx, y + 18), "!", font=font(SANS_B, 14), fill=(30, 30, 30),
           anchor="mm")
    d.arc([x + 6, y + 30, x + w - 6, y + 42], 0, 180, fill=(40, 90, 160), width=3)


def icon_energy(d, x, y, w, h):
    # lightning bolt
    cx = x + w // 2
    d.polygon([(cx + 4, y + 4), (cx - 8, y + 22), (cx - 1, y + 22),
               (cx - 4, y + 40), (cx + 9, y + 20), (cx + 1, y + 20)],
              fill=(240, 200, 40))


ICONS = {
    "CONFLICT": (icon_conflict, (250, 225, 200)),
    "JUSTICE": (icon_justice, (235, 225, 205)),
    "MARKETS": (icon_markets, (225, 235, 220)),
    "CLIMATE": (icon_climate, (220, 240, 225)),
    "POLITICS": (icon_politics, (220, 230, 245)),
    "SCIENCE": (icon_science, (230, 235, 250)),
    "TECH": (icon_tech, (230, 232, 240)),
    "ECONOMY": (icon_economy, (245, 235, 200)),
    "SOCIETY": (icon_society, (235, 228, 245)),
    "HEALTH": (icon_health, (245, 225, 225)),
    "SPACE": (icon_space, (225, 228, 248)),
    "DISASTER": (icon_disaster, (240, 232, 210)),
    "ENERGY": (icon_energy, (245, 240, 200)),
}


# ---- v2: one icon per story (not per category) ----
def icon_quake(d, x, y, w, h):
    # seismograph trace (Peru quake)
    d.rectangle([x + 4, y + 4, x + w - 4, y + h - 4], outline=(120, 120, 120))
    pts = [(x + 6, y + 24), (x + 14, y + 24), (x + 18, y + 12),
           (x + 22, y + 34), (x + 26, y + 18), (x + 30, y + 30),
           (x + 34, y + 10), (x + 38, y + 28), (x + 42, y + 24),
           (x + 50, y + 24)]
    d.line(pts, fill=(178, 34, 34), width=2)


def icon_badge(d, x, y, w, h):
    # police badge (cartel boss captured)
    cx, cy = x + w // 2, y + h // 2
    d.polygon([(cx, y + 5), (cx + 15, y + 12), (cx + 13, y + 30),
               (cx, y + 38), (cx - 13, y + 30), (cx - 15, y + 12)],
              fill=(40, 80, 160))
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 214, 90))


def icon_missile(d, x, y, w, h):
    # rocket with flame (missile strike)
    d.polygon([(x + 18, y + 34), (x + 30, y + 8), (x + 40, y + 34)],
              fill=(200, 60, 50))
    d.polygon([(x + 18, y + 34), (x + 24, y + 26), (x + 14, y + 30)],
              fill=(120, 120, 120))
    d.polygon([(x + 40, y + 34), (x + 34, y + 26), (x + 44, y + 30)],
              fill=(120, 120, 120))
    d.polygon([(x + 24, y + 36), (x + 29, y + 42), (x + 34, y + 36)],
              fill=(255, 180, 60))
    d.ellipse([x + 26, y + 16, x + 32, y + 22], fill=(255, 255, 255))


def icon_chart_down(d, x, y, w, h):
    # descending bars + down arrow (sell-off)
    for bx, bh in [(10, 32), (24, 24), (38, 14)]:
        d.rectangle([x + bx, y + h - 6 - bh, x + bx + 10, y + h - 6],
                    fill=(178, 34, 34))
    d.line([x + 6, y + 6, x + w - 8, y + 20], fill=(60, 60, 60), width=2)
    d.polygon([(x + w - 14, y + 14), (x + w - 4, y + 20),
               (x + w - 14, y + 24)], fill=(60, 60, 60))


def icon_summit(d, x, y, w, h):
    # two crossed flags (summit)
    d.line([x + 16, y + 8, x + 30, y + 38], fill=(60, 60, 60), width=2)
    d.line([x + 40, y + 8, x + 26, y + 38], fill=(60, 60, 60), width=2)
    d.polygon([(x + 16, y + 8), (x + 34, y + 12), (x + 16, y + 20)],
              fill=(178, 34, 34))
    d.polygon([(x + 40, y + 8), (x + 22, y + 12), (x + 40, y + 20)],
              fill=(40, 80, 160))


def icon_pi(d, x, y, w, h):
    # pi symbol (maths proof)
    d.text((x + w // 2, y + h // 2 - 2), "π", font=font(SERIF_B, 30),
           fill=(40, 60, 120), anchor="mm")
    d.text((x + w - 10, y + h - 8), "3.14", font=font(SANS_B, 8),
           fill=(90, 90, 90), anchor="rb")


def icon_ship(d, x, y, w, h):
    # cargo ship with containers
    d.rectangle([x + 14, y + 14, x + 24, y + 24], fill=(178, 34, 34))
    d.rectangle([x + 26, y + 14, x + 36, y + 24], fill=(40, 90, 160))
    d.rectangle([x + 38, y + 14, x + 46, y + 24], fill=(230, 170, 40))
    d.polygon([(x + 8, y + 26), (x + 50, y + 26), (x + 44, y + 36),
               (x + 14, y + 36)], fill=(60, 60, 60))
    d.line([x + 6, y + 40, x + 52, y + 40], fill=(40, 90, 160), width=2)


def icon_truck(d, x, y, w, h):
    # box truck with aid cross (food vehicle)
    d.rectangle([x + 8, y + 10, x + 36, y + 30], fill=(240, 240, 240),
                outline=(60, 60, 60))
    d.rectangle([x + 38, y + 16, x + 50, y + 30], fill=(178, 34, 34))
    d.rectangle([x + 41, y + 19, x + 47, y + 25], fill=(180, 220, 240))
    d.ellipse([x + 12, y + 30, x + 20, y + 38], fill=(30, 30, 30))
    d.ellipse([x + 40, y + 30, x + 48, y + 38], fill=(30, 30, 30))
    d.text((x + 22, y + 20), "+", font=font(SANS_B, 14), fill=(178, 34, 34),
           anchor="mm")


def icon_intercept(d, x, y, w, h):
    # two streaks meeting in a burst (interception)
    import math
    d.line([x + 6, y + 36, x + 26, y + 16], fill=(178, 34, 34), width=3)
    d.line([x + 50, y + 36, x + 30, y + 16], fill=(40, 80, 160), width=3)
    cx, cy = x + 28, y + 14
    pts = []
    for i in range(8):
        ang = i * math.pi / 4
        r = 9 if i % 2 == 0 else 4
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    d.polygon(pts, fill=(255, 200, 60))


def icon_stars(d, x, y, w, h):
    # circle of stars on blue (EU deal)
    import math
    cx, cy = x + w // 2, y + h // 2
    d.ellipse([cx - 20, cy - 18, cx + 20, cy + 18], fill=(40, 60, 140))
    for i in range(12):
        ang = i * math.pi / 6 - math.pi / 2
        sx, sy = cx + 14 * math.cos(ang), cy + 13 * math.sin(ang)
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 214, 90))


def icon_trade(d, x, y, w, h):
    # two-way trade arrows + crate
    d.line([x + 6, y + 14, x + 44, y + 14], fill=(40, 90, 160), width=3)
    d.polygon([(x + 44, y + 9), (x + 52, y + 14), (x + 44, y + 19)],
              fill=(40, 90, 160))
    d.line([x + 50, y + 30, x + 12, y + 30], fill=(178, 34, 34), width=3)
    d.polygon([(x + 12, y + 25), (x + 4, y + 30), (x + 12, y + 35)],
              fill=(178, 34, 34))
    d.rectangle([x + 22, y + 18, x + 34, y + 28], fill=(230, 170, 40),
                outline=(150, 115, 30))


def icon_server(d, x, y, w, h):
    # server rack (data centres)
    for i, yy in enumerate((8, 18, 28)):
        d.rectangle([x + 14, y + yy, x + 42, y + yy + 8], fill=(50, 54, 66))
        d.ellipse([x + 18, y + yy + 3, x + 21, y + yy + 6],
                  fill=(120, 220, 120) if i != 1 else (255, 200, 60))
        d.line([x + 26, y + yy + 4, x + 38, y + yy + 4],
               fill=(160, 160, 160), width=1)


def icon_lock(d, x, y, w, h):
    # padlock with a crack (database hacked)
    cx = x + w // 2
    d.arc([cx - 10, y + 6, cx + 10, y + 22], 180, 360, fill=(60, 60, 60),
          width=3)
    d.rectangle([cx - 14, y + 18, cx + 14, y + 38], fill=(178, 34, 34))
    d.ellipse([cx - 3, y + 24, cx + 3, y + 30], fill=(255, 255, 255))
    d.line([cx, y + 30, cx, y + 35], fill=(255, 255, 255), width=2)
    d.line([cx + 4, y + 20, cx - 2, y + 28], fill=(255, 255, 255), width=1)


def icon_robot(d, x, y, w, h):
    # robot head (AI weapons)
    cx, cy = x + w // 2, y + h // 2 + 2
    d.line([cx, y + 4, cx, y + 10], fill=(60, 60, 60), width=2)
    d.ellipse([cx - 3, y + 1, cx + 3, y + 7], fill=(178, 34, 34))
    d.rounded_rectangle([cx - 15, y + 10, cx + 15, y + 34], radius=4,
                        fill=(180, 190, 200), outline=(60, 60, 60))
    d.ellipse([cx - 9, y + 16, cx - 3, y + 22], fill=(40, 90, 160))
    d.ellipse([cx + 3, y + 16, cx + 9, y + 22], fill=(40, 90, 160))
    d.line([cx - 7, y + 28, cx + 7, y + 28], fill=(60, 60, 60), width=2)


def icon_passport(d, x, y, w, h):
    # passport with seal (diplomat expelled)
    d.rectangle([x + 14, y + 6, x + 42, y + 38], fill=(40, 60, 120))
    d.ellipse([x + 20, y + 14, x + 36, y + 30], outline=(255, 214, 90),
              width=2)
    d.text((x + 28, y + 22), "★", font=font(SANS_B, 10), fill=(255, 214, 90),
           anchor="mm")
    d.line([x + 20, y + 33, x + 36, y + 33], fill=(255, 255, 255), width=1)


def icon_gavel(d, x, y, w, h):
    # gavel + sound block (court sentence)
    d.polygon([(x + 14, y + 10), (x + 34, y + 6), (x + 36, y + 14),
               (x + 16, y + 18)], fill=(120, 80, 40))
    d.line([x + 26, y + 14, x + 44, y + 34], fill=(90, 60, 30), width=4)
    d.rectangle([x + 12, y + 34, x + 30, y + 40], fill=(90, 60, 30))


def icon_virus(d, x, y, w, h):
    # spiky virus (measles)
    import math
    cx, cy = x + w // 2, y + h // 2
    for i in range(10):
        ang = i * math.pi / 5
        d.line([cx + 10 * math.cos(ang), cy + 10 * math.sin(ang),
                cx + 15 * math.cos(ang), cy + 15 * math.sin(ang)],
               fill=(178, 34, 34), width=2)
    d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=(200, 60, 60))
    d.ellipse([cx - 4, cy - 4, cx - 1, cy - 1], fill=(255, 180, 180))
    d.ellipse([cx + 2, cy + 3, cx + 5, cy + 6], fill=(255, 180, 180))


def icon_mosquito(d, x, y, w, h):
    # mosquito (dengue)
    cx, cy = x + w // 2, y + h // 2
    d.ellipse([cx - 2, cy - 12, cx + 10, cy + 8], fill=(60, 60, 60))
    d.ellipse([cx - 10, cy - 14, cx - 2, cy - 2], fill=(200, 210, 220),
              outline=(120, 130, 140))
    d.ellipse([cx - 12, cy - 4, cx - 2, cy + 6], fill=(200, 210, 220),
              outline=(120, 130, 140))
    for dx, dy in [(-6, 10), (0, 12), (6, 10)]:
        d.line([cx + 2, cy + 6, cx + dx, cy + dy + 4], fill=(60, 60, 60),
               width=1)
    d.line([cx + 10, cy - 8, cx + 18, cy - 10], fill=(60, 60, 60), width=1)


def icon_pill(d, x, y, w, h):
    # capsule pill (cancer drug)
    cx, cy = x + w // 2, y + h // 2
    d.ellipse([cx - 18, cy - 8, cx + 2, cy + 8], fill=(178, 34, 34))
    d.rounded_rectangle([cx - 18, cy - 8, cx + 18, cy + 8], radius=8,
                        outline=(60, 60, 60))
    d.line([cx, cy - 8, cx, cy + 8], fill=(60, 60, 60), width=1)


def icon_hospital(d, x, y, w, h):
    # hospital bed + cross
    d.rectangle([x + 8, y + 24, x + 48, y + 30], fill=(90, 130, 180))
    d.line([x + 12, y + 30, x + 12, y + 38], fill=(60, 60, 60), width=2)
    d.line([x + 44, y + 30, x + 44, y + 38], fill=(60, 60, 60), width=2)
    d.ellipse([x + 10, y + 18, x + 18, y + 26], fill=(230, 200, 160))
    d.rectangle([x + 38, y + 8, x + 44, y + 20], fill=(178, 34, 34))
    d.rectangle([x + 33, y + 12, x + 49, y + 16], fill=(178, 34, 34))


def icon_boat(d, x, y, w, h):
    # capsized boat + waves
    d.polygon([(x + 10, y + 12), (x + 46, y + 20), (x + 40, y + 28),
               (x + 14, y + 22)], fill=(120, 80, 40))
    d.arc([x + 6, y + 28, x + 26, y + 40], 0, 180, fill=(40, 90, 160),
          width=2)
    d.arc([x + 30, y + 28, x + 50, y + 40], 0, 180, fill=(40, 90, 160),
          width=2)


def icon_barrel(d, x, y, w, h):
    # oil barrel + drop
    cx = x + w // 2
    d.rounded_rectangle([cx - 12, y + 10, cx + 12, y + 36], radius=3,
                        fill=(40, 60, 90))
    d.line([cx - 12, y + 17, cx + 12, y + 17], fill=(20, 30, 50), width=2)
    d.line([cx - 12, y + 29, cx + 12, y + 29], fill=(20, 30, 50), width=2)
    d.polygon([(x + 42, y + 16), (x + 48, y + 26), (x + 36, y + 26)],
              fill=(30, 30, 30))
    d.ellipse([x + 36, y + 24, x + 48, y + 34], fill=(30, 30, 30))


def icon_court(d, x, y, w, h):
    # courthouse (sentence)
    d.polygon([(x + 8, y + 12), (x + 48, y + 12), (x + 28, y + 4)],
              fill=(120, 100, 70))
    for px in (12, 24, 36):
        d.rectangle([x + px, y + 14, x + px + 6, y + 32],
                    fill=(150, 130, 95))
    d.rectangle([x + 8, y + 32, x + 48, y + 36], fill=(120, 100, 70))


def icon_tv(d, x, y, w, h):
    # television (broadcaster seized)
    d.line([x + 18, y + 6, x + 28, y + 12], fill=(60, 60, 60), width=2)
    d.line([x + 38, y + 6, x + 28, y + 12], fill=(60, 60, 60), width=2)
    d.rectangle([x + 10, y + 12, x + 46, y + 34], fill=(30, 30, 40))
    d.rectangle([x + 14, y + 16, x + 42, y + 30], fill=(90, 140, 200))
    d.line([x + 22, y + 36, x + 22, y + 40], fill=(60, 60, 60), width=2)
    d.line([x + 34, y + 36, x + 34, y + 40], fill=(60, 60, 60), width=2)


def icon_gamepad(d, x, y, w, h):
    # gamepad (GTA VI)
    cx, cy = x + w // 2, y + h // 2
    d.rounded_rectangle([cx - 20, cy - 10, cx + 20, cy + 10], radius=8,
                        fill=(40, 44, 60))
    d.rectangle([cx - 14, cy - 2, cx - 6, cy + 2], fill=(255, 255, 255))
    d.rectangle([cx - 12, cy - 4, cx - 8, cy + 4], fill=(255, 255, 255))
    d.ellipse([cx + 8, cy - 5, cx + 13, cy], fill=(255, 200, 60))
    d.ellipse([cx + 13, cy, cx + 18, cy + 5], fill=(178, 34, 34))


def icon_crown(d, x, y, w, h):
    # crown (Princess of Wales)
    cx = x + w // 2
    d.polygon([(cx - 16, y + 30), (cx - 16, y + 14), (cx - 8, y + 22),
               (cx, y + 8), (cx + 8, y + 22), (cx + 16, y + 14),
               (cx + 16, y + 30)], fill=(230, 180, 40),
              outline=(150, 115, 30))
    d.rectangle([cx - 16, y + 30, cx + 16, y + 35], fill=(230, 180, 40),
                outline=(150, 115, 30))
    for jx, jy in [(-16, 12), (0, 6), (16, 12)]:
        d.ellipse([cx + jx - 2, y + jy, cx + jx + 2, y + jy + 4],
                  fill=(178, 34, 34))


def icon_tennis(d, x, y, w, h):
    # tennis ball
    cx, cy = x + w // 2, y + h // 2
    d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=(200, 220, 60))
    d.arc([cx - 20, cy - 13, cx + 6, cy + 13], 300, 60,
          fill=(255, 255, 255), width=2)
    d.arc([cx - 6, cy - 13, cx + 20, cy + 13], 120, 240,
          fill=(255, 255, 255), width=2)


def icon_basketball(d, x, y, w, h):
    # basketball
    cx, cy = x + w // 2, y + h // 2
    d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=(230, 120, 40))
    d.line([cx - 13, cy, cx + 13, cy], fill=(60, 30, 10), width=2)
    d.line([cx, cy - 13, cx, cy + 13], fill=(60, 30, 10), width=2)
    d.arc([cx - 13, cy - 13, cx + 13, cy + 13], 300, 60,
          fill=(60, 30, 10), width=2)
    d.arc([cx - 13, cy - 13, cx + 13, cy + 13], 120, 240,
          fill=(60, 30, 10), width=2)


def icon_candle(d, x, y, w, h):
    # memorial candle (obituary)
    cx = x + w // 2
    d.rectangle([cx - 5, y + 16, cx + 5, y + 36], fill=(240, 240, 235),
                outline=(150, 150, 140))
    d.line([cx, y + 12, cx, y + 16], fill=(60, 60, 60), width=1)
    d.ellipse([cx - 4, y + 2, cx + 4, y + 12], fill=(255, 180, 60))
    d.ellipse([cx - 2, y + 5, cx + 2, y + 11], fill=(255, 230, 120))
    d.line([cx - 12, y + 38, cx + 12, y + 38], fill=(150, 150, 140), width=2)


def icon_rugby(d, x, y, w, h):
    # rugby ball
    cx, cy = x + w // 2, y + h // 2
    d.ellipse([cx - 18, cy - 10, cx + 18, cy + 10], fill=(150, 90, 50))
    d.line([cx - 8, cy, cx + 8, cy], fill=(255, 255, 255), width=2)
    for lx in (-6, -2, 2, 6):
        d.line([cx + lx, cy - 3, cx + lx, cy + 3], fill=(255, 255, 255),
               width=1)


def icon_wave(d, x, y, w, h):
    # sea waves (quake off Timor)
    for yy in (12, 22, 32):
        d.arc([x + 6, y + yy, x + 26, y + yy + 12], 180, 360,
              fill=(40, 90, 160), width=2)
        d.arc([x + 30, y + yy, x + 50, y + yy + 12], 180, 360,
              fill=(40, 90, 160), width=2)


# v2: one icon per story, keyed by headline (falls back to the category
# icon when a headline has no entry here).
STORY_ICONS = {
    "Magnitude 6.7 quake shakes central Peru": (icon_quake, (240, 232, 210)),
    "Mexico captures FBI most-wanted cartel boss": (icon_badge, (235, 225, 205)),
    "Russian missile hits Zelensky's hometown": (icon_missile, (250, 225, 200)),
    "AI sell-off pushes US stocks into correction": (icon_chart_down, (225, 235, 220)),
    "COP31 talks run past deadline": (icon_climate, (220, 240, 225)),
    "Trump defends Putin ties; Zelensky calls Putin a killer": (icon_summit, (220, 230, 245)),
    "Anthropic mathematician claims AI-assisted Riemann proof": (icon_pi, (230, 235, 250)),
    "Drones hit Russian cargo ship in Gulf of Finland": (icon_ship, (225, 235, 245)),
    "Israeli strike kills three in Gaza food vehicle": (icon_truck, (245, 235, 220)),
    "Houthis and Saudi coalition trade strikes": (icon_intercept, (250, 230, 210)),
    "UK and EU sign three post-Brexit deals": (icon_stars, (225, 228, 248)),
    "EU and Indonesia sign trade deal": (icon_trade, (245, 235, 200)),
    "Trump threatens tax on firms building data centers abroad": (icon_server, (230, 232, 240)),
    "FBI crime database reportedly hacked": (icon_lock, (240, 228, 228)),
    "UN talks agree to keep working on AI weapons rules": (icon_robot, (235, 232, 245)),
    "Denmark expels Russian diplomat over alleged plot": (icon_passport, (228, 235, 245)),
    "French police sentenced over racist beating": (icon_gavel, (238, 230, 220)),
    "US child dies of measles in Virginia": (icon_virus, (245, 225, 225)),
    "Mosquitoes with bacterium cut dengue in Brazil": (icon_mosquito, (235, 245, 230)),
    "Pill shows progress against pancreatic cancer": (icon_pill, (245, 235, 240)),
    "BepiColombo reaches Mercury orbit after eight years": (icon_space, (225, 228, 248)),
    "Bolsonaro in intensive care": (icon_hospital, (240, 232, 232)),
    "Boat of funeral mourners capsizes in Nigeria": (icon_boat, (225, 235, 245)),
    "Gulf economies hit by Iran war": (icon_barrel, (245, 240, 200)),
    "Indian man sentenced over plot to kill Sikh leader": (icon_court, (235, 228, 210)),
    "Turkey takes control of Sozcu TV": (icon_tv, (230, 235, 245)),
    "Nvidia chief ousted; Trump says he discussed it with Xi": (icon_tech, (230, 232, 240)),
    "GTA VI earns $3.8 billion on first day": (icon_gamepad, (235, 230, 248)),
    "Princess Kate says she is in remission": (icon_crown, (248, 240, 210)),
    "Alcaraz to face Zverev in ATP Finals final": (icon_tennis, (235, 245, 210)),
    "Harden scores 51 and passes Kobe Bryant": (icon_basketball, (250, 230, 200)),
    "CERN finds first evidence of ultra-rare decay": (icon_science, (230, 235, 250)),
    "Phumzile Mlambo-Ngcuka dies aged 71": (icon_candle, (240, 235, 225)),
    "Wallabies beat Wales 29-26 in Cardiff": (icon_rugby, (240, 235, 200)),
    "Magnitude 6.8 quake off Timor": (icon_wave, (225, 238, 245)),
}

# ---------------------------------------------------------------- stories
# v3 — newspaper layout (own design: masthead + stat strip + region bar +
# 3 big panels + 10 medium cards + world map + numbered list + date check).
# All headlines/summaries are written here, from the v3 spec. Stories that
# did not happen (or were not first reported) on 21 Nov 2026 are left out
# on purpose — see the DATE CHECK box.
import math

SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"

STATS = [
    ("6.7", "magnitude of the Peru quake in Junín"),
    ("5", "missiles shot down over Saudi Arabia"),
    ("11", "dead after Chapo Isidro's capture"),
    ("4", "killed in the Basra power station fire"),
    ("700,000", "displaced in southern Ethiopia"),
    ("$3.8bn", "GTA VI's first-day earnings"),
]

REGIONS = [
    ("Americas", 10, (150, 60, 60)),
    ("Europe", 12, (60, 90, 150)),
    ("Middle East", 6, (180, 120, 40)),
    ("Asia", 3, (60, 140, 90)),
    ("Africa", 2, (140, 90, 40)),
    ("Oceania", 1, (40, 120, 140)),
    ("Global", 1, (110, 110, 110)),
]

# (num, category, dateline, headline, summary, data chip, sources)
PANELS = [
    (1, "CONFLICT", "BAHRAIN · MIDDLE EAST",
     "Iran strikes US bases in Bahrain",
     "Tehran says it hit two US positions; Bahrain reports a fire at a "
     "civilian site, no injuries.",
     "2 positions hit · no injuries", "AFP, Reuters"),
    (2, "DISASTER", "JUNÍN, PERU · EARTHQUAKE",
     "Magnitude 6.7 earthquake shakes central Peru",
     "The deep quake near Carhuamayo was felt in Lima and along the coast; "
     "no deaths, damage or tsunami risk reported.",
     "00:09 UTC · 108 km deep", "USGS, IGP"),
    (3, "CLIMATE", "ANTALYA, TÜRKIYE",
     "Climate summit runs into Saturday with no deal",
     "COP31 missed its Friday close with no deal on fossil fuels; a third "
     "text is promised.",
     "No deal · day 13", "AFP, Al Jazeera"),
]

# (num, category, dateline, headline, summary, source)
MEDIUM = [
    (4, "JUSTICE", "MEXICO",
     "Mexico captures FBI most-wanted cartel boss",
     "Chapo Isidro seized; 11 die in the aftermath.", "Wire reports"),
    (5, "CONFLICT", "KYIV, UKRAINE",
     "Russian missile hits Zelensky's hometown",
     "Two die in Kryvyi Rih strike.", "Wire reports"),
    (6, "CONFLICT", "RIYADH, SAUDI ARABIA",
     "Five Houthi missiles shot down over Saudi Arabia",
     "Three destroyed over Riyadh, two over Jizan.", "Wire reports"),
    (7, "POLITICS", "WASHINGTON, US",
     "Trump defends Putin ties; Zelensky calls Putin a killer",
     "After Shenzhen, Trump defends his Putin ties.", "Wire reports"),
    (8, "GAMES", "WORLD",
     "GTA VI earns $3.8 billion on first day",
     "Biggest entertainment launch ever.", "BBC Business"),
    (9, "CULTURE", "LONDON, UK",
     "Princess Kate says she is in remission",
     "Princess of Wales announces she is in remission from cancer.",
     "CBS News"),
    (10, "SPORTS", "TURIN, ITALY",
     "Alcaraz to face Zverev in ATP Finals final",
     "Alcaraz beats Shelton in three sets; final on Sunday.", "BBC Sport"),
    (11, "SPORTS", "CLEVELAND, US",
     "Harden scores 51 and passes Kobe Bryant",
     "Harden's 26th career 50-point game, passing Kobe.",
     "Guardian Sport"),
    (12, "SCIENCE", "GENEVA, SWITZERLAND",
     "CERN finds first evidence of ultra-rare decay",
     "First evidence of an extremely rare particle decay.", "Phys.org"),
    (13, "SPORTS", "CARDIFF, WALES",
     "Wallabies beat Wales 29-26 in Cardiff",
     "Australia ends a four-match losing streak.", "BBC Sport"),
]

# (num, place, headline, source) — map pins + numbered list, stories 14-35
LISTED = [
    (14, "Dili", "Magnitude 6.8 quake off Timor", "Yonhap"),
    (15, "Basra", "Fire at power station kills four", "Reuters"),
    (16, "Cape Town", "Mlambo-Ngcuka dies aged 71", "Africanews"),
    (17, "Addis Ababa", "700,000 displaced in southern Ethiopia",
     "France 24"),
    (18, "New Delhi", "Nepal PM to visit India", "BBC"),
    (19, "Tallinn", "Estonia to close Russia border crossings",
     "Straits Times"),
    (20, "Seoul", "Ruling party moves to impeach chief justice", "Yonhap"),
    (21, "New York", "Mamdani plans to close Rikers by 2032", "BBC"),
    (22, "Madrid", "Spain heads to Nov. 29 election", "El País"),
    (23, "Paris", "France probes Depardieu and Houellebecq", "BBC"),
    (24, "Texas", "Inmate cried out during hour-long execution", "BBC"),
    (25, "US", "YouTube nears multibillion-dollar school deal",
     "Straits Times"),
    (26, "Paris", "Villepin announces French presidential run",
     "France 24"),
    (27, "Calgary", "Cavalry FC wins Canadian Premier League title",
     "CBC Sports"),
    (28, "Austria", "Colturi wins Albania's first ski World Cup race",
     "CBC Sports"),
    (29, "Cornwall", "Spitting Image co-creator Peter Fluck dies at 85",
     "BBC"),
    (30, "Abu Dhabi", "New fossil carnivore found in the UAE",
     "The National"),
    (31, "Strait of Hormuz", "Lewis Pugh swims the strait",
     "Wire reports"),
    (32, "Gaza", "Israeli strike kills three in Gaza food vehicle",
     "Wire reports"),
    (33, "Washington", "FBI crime database reportedly hacked",
     "Wire reports"),
    (34, "Copenhagen", "Denmark expels Russian diplomat", "Wire reports"),
    (35, "Washington", "Nvidia chief out; Trump raised it with Xi",
     "Wire reports"),
]

# map pin positions: num -> (lon, lat)
PIN_POS = {
    14: (125.6, -8.6), 15: (47.8, 30.5), 16: (18.4, -33.9),
    17: (38.7, 9.0), 18: (77.2, 28.6), 19: (24.7, 59.4),
    20: (127.0, 37.5), 21: (-74.0, 40.7), 22: (-3.7, 40.4),
    23: (2.35, 48.85), 24: (-99.0, 31.0), 25: (-122.4, 37.6),
    26: (2.35, 48.85), 27: (-114.0, 51.0), 28: (14.4, 47.5),
    29: (-5.0, 50.2), 30: (54.4, 24.5), 31: (56.5, 26.5),
    32: (34.5, 31.5), 33: (-77.0, 38.9), 34: (12.6, 55.7),
    35: (-77.0, 38.9),
}

# pin nudges (dx, dy) in px, to separate pins that would overlap
# (computed so every pair of pins is >=18 px apart)
PIN_OFF = {
    15: (-2, -15), 17: (0, 7), 18: (5, -1), 19: (8, -3),
    21: (10, -7), 22: (-5, 19), 23: (8, -18), 24: (-3, 1),
    25: (-2, 2), 26: (-15, 9), 27: (1, -2), 28: (7, 11),
    29: (-7, -11), 30: (5, 14), 31: (2, -3), 32: (2, 11),
    33: (0, 12), 34: (-6, 7), 35: (-7, -6),
}

# simplified continents, as (lon, lat) polygons
CONTINENTS = [
    [(-168, 66), (-150, 61), (-140, 60), (-135, 58), (-130, 54),
     (-125, 49), (-124, 42), (-120, 34), (-114, 29), (-110, 24),
     (-105, 20), (-97, 16), (-94, 17), (-90, 14), (-86, 12),
     (-83, 9), (-79, 9), (-77, 8), (-80, 10), (-82, 15),
     (-84, 16), (-87, 21), (-90, 21), (-91, 19), (-96, 19),
     (-97, 26), (-93, 30), (-89, 30), (-84, 30), (-81, 25),
     (-80, 32), (-76, 35), (-75, 39), (-74, 40), (-70, 42),
     (-68, 44), (-66, 45), (-60, 47), (-55, 52), (-60, 55),
     (-65, 60), (-68, 58), (-75, 62), (-78, 62), (-85, 66),
     (-92, 66), (-95, 69), (-110, 68), (-125, 71), (-140, 70),
     (-155, 71), (-165, 68), (-168, 66)],
    [(-58, 64), (-52, 60), (-43, 60), (-40, 64), (-32, 68),
     (-22, 70), (-25, 74), (-35, 76), (-50, 76), (-58, 74),
     (-60, 70), (-58, 64)],
    [(-79, 9), (-77, 7), (-75, 10), (-72, 11), (-68, 11),
     (-64, 10), (-60, 8), (-55, 6), (-51, 4), (-50, 0),
     (-44, -3), (-38, -5), (-35, -8), (-35, -15), (-38, -20),
     (-40, -25), (-48, -28), (-52, -33), (-57, -38), (-62, -41),
     (-65, -45), (-68, -50), (-70, -54), (-73, -50), (-73, -44),
     (-73, -37), (-71, -30), (-70, -20), (-75, -15), (-79, -8),
     (-81, -3), (-80, 3), (-79, 9)],
    [(-10, 36), (-9, 38), (-9, 43), (-4, 44), (-2, 47), (-4, 48),
     (-1, 50), (2, 51), (4, 53), (7, 55), (8, 57), (10, 59),
     (13, 58), (18, 56), (21, 55), (24, 58), (26, 59), (28, 60),
     (30, 62), (28, 65), (25, 66), (22, 68), (18, 69), (15, 68),
     (13, 65), (10, 62), (6, 62), (5, 60), (5, 58), (8, 57),
     (10, 54), (8, 52), (5, 50), (3, 47), (0, 44), (3, 42),
     (7, 44), (10, 44), (13, 45), (16, 44), (18, 40), (20, 40),
     (22, 38), (24, 37), (26, 38), (28, 40), (30, 41), (30, 36),
     (27, 36), (23, 36), (19, 40), (16, 38), (12, 38), (8, 37),
     (3, 38), (0, 36), (-5, 36), (-10, 36)],
    [(-17, 15), (-16, 20), (-15, 25), (-12, 28), (-8, 31), (-5, 35),
     (0, 36), (5, 37), (10, 37), (12, 34), (15, 32), (19, 32),
     (23, 32), (27, 31), (30, 31), (32, 31), (34, 29), (36, 26),
     (37, 22), (39, 18), (41, 14), (43, 11), (46, 11), (51, 12),
     (51, 10), (48, 5), (44, 0), (41, -4), (40, -10), (39, -16),
     (37, -20), (35, -24), (33, -27), (30, -30), (27, -33),
     (23, -35), (19, -35), (17, -32), (15, -28), (13, -22),
     (12, -16), (13, -10), (12, -5), (9, 4), (4, 6), (0, 5),
     (-5, 5), (-8, 4), (-12, 8), (-15, 11), (-17, 15)],
    [(30, 36), (33, 36), (36, 36), (39, 38), (42, 40), (45, 41),
     (48, 42), (51, 44), (55, 45), (58, 45), (62, 45), (66, 44),
     (70, 46), (74, 48), (78, 52), (82, 56), (86, 60), (90, 62),
     (95, 64), (100, 66), (105, 68), (110, 70), (115, 72),
     (120, 73), (125, 72), (130, 72), (135, 71), (140, 72),
     (145, 71), (150, 70), (155, 69), (160, 69), (165, 67),
     (170, 66), (175, 65), (178, 65), (178, 62), (175, 60),
     (170, 60), (165, 60), (162, 58), (158, 53), (155, 50),
     (152, 46), (148, 43), (144, 40), (141, 38), (139, 35),
     (136, 33), (133, 34), (130, 33), (127, 35), (126, 38),
     (122, 40), (120, 36), (118, 31), (115, 28), (112, 23),
     (110, 20), (108, 15), (106, 10), (104, 8), (101, 7),
     (99, 10), (97, 14), (95, 16), (93, 20), (91, 22),
     (89, 22), (87, 21), (85, 19), (83, 18), (80, 15),
     (78, 10), (76, 9), (75, 13), (73, 19), (71, 22),
     (69, 23), (67, 25), (64, 25), (61, 25), (58, 26),
     (56, 27), (54, 27), (52, 28), (50, 29), (48, 30),
     (47, 30), (44, 29), (42, 27), (40, 24), (38, 20),
     (36, 18), (35, 21), (35, 25), (34, 28), (33, 30),
     (32, 31), (30, 33), (30, 36)],
    [(114, -22), (114, -28), (115, -32), (115, -35), (118, -35),
     (122, -34), (125, -32), (129, -32), (132, -32), (135, -35),
     (138, -35), (140, -38), (143, -39), (146, -39), (149, -37),
     (150, -36), (153, -32), (153, -28), (151, -24), (149, -20),
     (146, -19), (143, -17), (142, -14), (142, -11), (139, -13),
     (136, -12), (135, -15), (132, -12), (130, -13), (127, -14),
     (124, -15), (121, -17), (118, -20), (114, -22)],
    [(109, 1), (111, 2), (114, 4), (117, 6), (119, 3), (119, 0),
     (117, -2), (114, -4), (111, -3), (109, 1)],
    [(131, -1), (134, -2), (137, -3), (141, -3), (144, -4),
     (147, -6), (150, -9), (147, -8), (143, -8), (139, -7),
     (135, -5), (132, -3), (131, -1)],
    [(95, 5), (98, 3), (100, 0), (103, -3), (105, -5), (103, -4),
     (100, -2), (97, 1), (95, 5)],
    [(105, -6), (108, -7), (111, -7), (114, -8), (114, -9),
     (110, -8), (106, -7), (105, -6)],
]


def _project(lon, lat, mx0, my0, mw, mh):
    # lon -170..190 -> x, lat 75..-55 -> y
    return (mx0 + (lon + 170) * mw / 360.0,
            my0 + (75 - lat) * mh / 130.0)


def icon_thumb(headline, size):
    """Render a v2 story icon at native size, downscale to a thumbnail."""
    entry = STORY_ICONS.get(headline)
    if entry is None:
        entry = ICONS.get("SPACE", (icon_space, (225, 228, 248)))
    fn, bg = entry
    tmp = Image.new("RGB", (56, 44), bg)
    td = ImageDraw.Draw(tmp)
    fn(td, 0, 0, 56, 44)
    return tmp.resize((size, max(1, round(size * 44 / 56))), Image.LANCZOS)


def art_bahrain(d, x0, y0, w, h):
    # dusk sky over the Gulf: purple -> orange, sun, skyline, smoke, sea
    top, mid, bot = (43, 38, 74), (150, 70, 55), (232, 158, 76)
    horizon = y0 + int(h * 0.58)
    for yy in range(y0, horizon):
        t = (yy - y0) / max(1, horizon - y0)
        c = lerp(lerp(top, mid, min(t * 2, 1)), bot, max(0, t * 2 - 1)) \
            if t < 0.5 else lerp(mid, bot, (t - 0.5) * 2)
        d.line([x0, yy, x0 + w, yy], fill=c)
    sx, sy = x0 + int(w * 0.10), y0 + int(h * 0.30)
    d.ellipse([sx - 13, sy - 13, sx + 13, sy + 13], fill=(255, 233, 168))
    d.ellipse([sx - 8, sy - 8, sx + 8, sy + 8], fill=(255, 246, 210))
    sky = [(0.56, 0.30), (0.63, 0.44), (0.70, 0.26), (0.77, 0.48),
           (0.84, 0.34), (0.91, 0.40)]
    for fx, fh in sky:
        bx = x0 + int(w * fx)
        bw = max(6, int(w * 0.055))
        bh = int((horizon - y0) * fh)
        d.rectangle([bx, horizon - bh, bx + bw, horizon], fill=(26, 22, 44))
    for fx, fh in sky[::2]:
        bx = x0 + int(w * fx)
        bh = int((horizon - y0) * fh)
        for wy in range(horizon - bh + 6, horizon - 4, 10):
            d.rectangle([bx + 3, wy, bx + 6, wy + 4], fill=(255, 214, 120))
    # smoke plume from a fire at the horizon, tapering up, leaning left
    fx = x0 + int(w * 0.32)
    for ry, rw, drift in [(0, 30, 0), (-10, 24, -4), (-19, 18, -8),
                          (-27, 13, -12), (-33, 9, -15)]:
        cy = horizon + ry - 7
        d.ellipse([fx + drift - rw // 2, cy, fx + drift + rw // 2, cy + 12],
                  fill=(206, 199, 193))
    d.ellipse([fx - 13, horizon - 8, fx + 13, horizon + 2],
              fill=(255, 140, 50))
    d.ellipse([fx - 7, horizon - 5, fx + 7, horizon + 1],
              fill=(255, 210, 90))
    # sea
    d.rectangle([x0, horizon, x0 + w, y0 + h], fill=(22, 50, 74))
    for wy in range(horizon + 6, y0 + h - 4, 10):
        d.line([x0 + 6, wy, x0 + 90, wy], fill=(70, 120, 150), width=1)
        d.line([x0 + int(w * 0.55), wy + 4, x0 + int(w * 0.75), wy + 4],
               fill=(70, 120, 150), width=1)
    # bright ship on the sea, right side
    sh_y = horizon + 10
    hx0 = x0 + int(w * 0.66)
    hx1 = x0 + int(w * 0.96)
    d.line([hx0 - 28, sh_y + 14, hx0 + 10, sh_y + 14],
           fill=(240, 244, 246), width=2)
    d.line([hx0 - 18, sh_y + 18, hx0 + 10, sh_y + 18],
           fill=(220, 230, 236), width=2)
    d.polygon([(hx0, sh_y), (hx1, sh_y), (hx1 - 12, sh_y + 12),
               (hx0 + 8, sh_y + 12)], fill=(168, 182, 196))
    d.polygon([(hx0, sh_y), (hx1, sh_y), (hx1 - 12, sh_y + 12),
               (hx0 + 8, sh_y + 12)], outline=(60, 72, 84))
    d.rectangle([hx0 + 30, sh_y - 12, hx0 + 62, sh_y], fill=(238, 240, 242))
    d.rectangle([hx0 + 30, sh_y - 12, hx0 + 62, sh_y],
                outline=(90, 100, 112))
    for wx in (36, 46, 56):
        d.rectangle([hx0 + wx, sh_y - 8, hx0 + wx + 5, sh_y - 3],
                    fill=(40, 60, 84))
    d.rectangle([hx0 + 68, sh_y - 18, hx0 + 76, sh_y], fill=(200, 60, 50))
    d.line([hx0 + 46, sh_y - 22, hx0 + 46, sh_y - 12],
           fill=(238, 240, 242), width=2)


def art_peru(d, x0, y0, w, h):
    # warm Andean morning: pale sky, dark ridges, red seismograph trace
    for yy in range(h):
        t = yy / h
        d.line([x0, y0 + yy, x0 + w, y0 + yy],
               fill=lerp((238, 228, 205), (214, 196, 160), t))
    gy = y0 + int(h * 0.72)
    d.rectangle([x0, gy, x0 + w, y0 + h], fill=(190, 170, 140))
    d.polygon([(x0, gy), (x0 + int(w * 0.18), y0 + int(h * 0.30)),
               (x0 + int(w * 0.38), gy)], fill=(120, 95, 70))
    d.polygon([(x0 + int(w * 0.30), gy), (x0 + int(w * 0.52),
               y0 + int(h * 0.18)), (x0 + int(w * 0.72), gy)],
              fill=(100, 80, 58))
    d.polygon([(x0 + int(w * 0.62), gy), (x0 + int(w * 0.82),
               y0 + int(h * 0.38)), (x0 + w, gy)], fill=(130, 105, 78))
    d.polygon([(x0 + int(w * 0.48), y0 + int(h * 0.24)),
               (x0 + int(w * 0.52), y0 + int(h * 0.18)),
               (x0 + int(w * 0.56), y0 + int(h * 0.24))],
              fill=(245, 245, 240))
    # seismograph trace across the sky (stops before the house)
    mid = y0 + int(h * 0.48)
    pts = [(x0 + 6, mid), (x0 + 30, mid), (x0 + 40, mid - 14),
           (x0 + 48, mid + 12), (x0 + 56, mid - 6), (x0 + 66, mid + 8),
           (x0 + 76, mid), (x0 + 110, mid), (x0 + 120, mid - 22),
           (x0 + 130, mid + 18), (x0 + 140, mid - 10), (x0 + 150, mid + 6),
           (x0 + 160, mid), (x0 + 200, mid), (x0 + 210, mid - 12),
           (x0 + 218, mid + 10), (x0 + int(w * 0.68), mid)]
    d.line(pts, fill=(178, 34, 34), width=3)
    # small house at the right, on the ground
    hx = x0 + int(w * 0.78)
    hy = gy - 26
    d.rectangle([hx, hy + 10, hx + 44, gy], fill=(245, 242, 235))
    d.polygon([(hx - 4, hy + 12), (hx + 22, hy - 4), (hx + 48, hy + 12)],
              fill=(178, 60, 50))
    d.rectangle([hx + 18, hy + 18, hx + 28, gy], fill=(90, 70, 50))
    d.rectangle([hx + 6, hy + 14, hx + 12, hy + 20], fill=(60, 80, 110))
    # crack in the ground
    d.line([(x0 + int(w * 0.10), gy + 8), (x0 + int(w * 0.16), gy + 14),
            (x0 + int(w * 0.22), gy + 9), (x0 + int(w * 0.30), gy + 15)],
           fill=(90, 70, 50), width=2)


def art_cop31(d, x0, y0, w, h):
    # globe + thermometer + clock near midnight (overtime)
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(222, 236, 226))
    gx, gy = x0 + int(w * 0.20), y0 + h // 2
    d.ellipse([gx - 34, gy - 34, gx + 34, gy + 34], fill=(70, 130, 180))
    d.ellipse([gx - 18, gy - 22, gx + 2, gy - 2], fill=(90, 160, 90))
    d.ellipse([gx - 4, gy + 6, gx + 20, gy + 24], fill=(90, 160, 90))
    d.ellipse([gx + 8, gy - 28, gx + 26, gy - 10], fill=(90, 160, 90))
    d.arc([gx - 34, gy - 34, gx + 34, gy + 34], 200, 340,
          fill=(200, 225, 240), width=3)
    tx = x0 + int(w * 0.50)
    d.rounded_rectangle([tx - 7, y0 + 14, tx + 7, y0 + h - 18], radius=7,
                        fill=(255, 255, 255), outline=(120, 120, 120))
    d.rectangle([tx - 3, y0 + 34, tx + 3, y0 + h - 22], fill=(200, 60, 50))
    d.ellipse([tx - 11, y0 + h - 30, tx + 11, y0 + h - 8],
              fill=(200, 60, 50))
    d.ellipse([tx - 11, y0 + h - 30, tx + 11, y0 + h - 8],
              outline=(120, 120, 120))
    cx, cy = x0 + int(w * 0.84), y0 + h // 2
    d.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=(255, 255, 255),
              outline=(60, 60, 60), width=2)
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        d.line([cx + 20 * math.cos(a), cy + 20 * math.sin(a),
                cx + 23 * math.cos(a), cy + 23 * math.sin(a)],
               fill=(60, 60, 60), width=1)
    d.line([cx, cy, cx - 7, cy - 11], fill=(30, 30, 30), width=3)
    d.line([cx, cy, cx + 2, cy - 18], fill=(178, 34, 34), width=2)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(30, 30, 30))


def draw_panel(d, x0, y0, w, h, panel):
    num, cat, dateline, headline, summary, chip, source = panel
    if num == 1:
        art_bahrain(d, x0, y0, w, 96)
    elif num == 2:
        art_peru(d, x0, y0, w, 96)
    else:
        art_cop31(d, x0, y0, w, 96)
    d.rectangle([x0, y0 + 96, x0 + w, y0 + 116], fill=RED)
    d.text((x0 + 10, y0 + 106), f"{num} · {cat}", font=font(SANS_B, 12),
           fill=(255, 255, 255), anchor="lm")
    d.text((x0 + 10, y0 + 126), dateline, font=font(SANS_B, 9),
           fill=(90, 90, 90), anchor="lm")
    hl = wrap(d, headline, font(SERIF_B, 13), w - 20)
    assert len(hl) <= 2 and not any("…" in ln for ln in hl), headline
    hy = y0 + 140
    for line in hl:
        d.text((x0 + 10, hy), line, font=font(SERIF_B, 13), fill=INK,
               anchor="lm")
        hy += 16
    sm = wrap(d, summary, font(SANS, 9), w - 20)
    assert len(sm) <= 2 and not any("…" in ln for ln in sm), summary
    sy = hy + 4
    for line in sm:
        d.text((x0 + 10, sy), line, font=font(SANS, 9), fill=(60, 60, 60),
               anchor="lm")
        sy += 12
    cy = y0 + h - 18
    chip_f = font(SANS_B, 9)
    cw = int(d.textlength(chip, font=chip_f)) + 16
    d.rounded_rectangle([x0, cy, x0 + cw, cy + 16], radius=8,
                        fill=(235, 230, 220))
    d.text((x0 + 8, cy + 8), chip, font=chip_f, fill=INK, anchor="lm")
    d.text((x0 + w - 8, cy + 8), f"({source})", font=font(SANS, 9),
           fill=(120, 120, 120), anchor="rm")


def draw_medium(img, x0, y0, w, h, med):
    d = ImageDraw.Draw(img)
    num, cat, dateline, headline, summary, source = med
    d.rectangle([x0, y0, x0 + w, y0 + 16], fill=RED)
    d.text((x0 + 8, y0 + 8), f"{num} · {cat}", font=font(SANS_B, 10),
           fill=(255, 255, 255), anchor="lm")
    d.text((x0 + 8, y0 + 26), dateline, font=font(SANS_B, 9),
           fill=(90, 90, 90), anchor="lm")
    hl = wrap(d, headline, font(SERIF_B, 11), w - 16)
    assert len(hl) <= 2 and not any("…" in ln for ln in hl), headline
    hy = y0 + 38
    for line in hl:
        d.text((x0 + 8, hy), line, font=font(SERIF_B, 11), fill=INK,
               anchor="lm")
        hy += 13
    sm = wrap(d, summary, font(SANS, 9), w - 16)
    assert len(sm) <= 2 and not any("…" in ln for ln in sm), summary
    sy = hy + 3
    for line in sm:
        d.text((x0 + 8, sy), line, font=font(SANS, 9), fill=(60, 60, 60),
               anchor="lm")
        sy += 11
    thumb = icon_thumb(headline, 34)
    img.paste(thumb, (x0 + 8, y0 + h - 30))
    d.text((x0 + 50, y0 + h - 16), f"({source})", font=font(SANS, 9),
           fill=(120, 120, 120), anchor="lm")


def draw_map(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(203, 218, 226))
    for poly in CONTINENTS:
        pts = [_project(lon, lat, x0, y0, w, h) for lon, lat in poly]
        d.polygon(pts, fill=(222, 206, 172), outline=(190, 175, 140))
    for num, place, hl, src in LISTED:
        lon, lat = PIN_POS[num]
        px, py = _project(lon, lat, x0, y0, w, h)
        dx, dy = PIN_OFF.get(num, (0, 0))
        px, py = px + dx, py + dy
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED,
                  outline=(255, 255, 255), width=1)
        d.text((px, py), str(num), font=font(SANS_B, 7),
               fill=(255, 255, 255), anchor="mm")


def draw_list(d, x0, y0, col_w, items):
    fb = font(SANS_B, 9)
    fr = font(SANS, 9)
    for i, (num, place, hl, src) in enumerate(items):
        yy = y0 + i * 16
        total = (d.textlength(str(num), font=fb)
                 + d.textlength(" ", font=fr)
                 + d.textlength(place + " — ", font=fb)
                 + d.textlength(hl, font=fr)
                 + d.textlength(" (" + src + ")", font=fr))
        assert total <= col_w, f"list line too long ({total:.0f}>{col_w}): {hl}"
        x = x0
        d.text((x, yy + 8), str(num), font=fb, fill=RED, anchor="lm")
        x += d.textlength(str(num) + " ", font=fr)
        d.text((x, yy + 8), place + " — ", font=fb, fill=INK, anchor="lm")
        x += d.textlength(place + " — ", font=fb)
        d.text((x, yy + 8), hl, font=fr, fill=INK, anchor="lm")
        x += d.textlength(hl, font=fr)
        d.text((x, yy + 8), " (" + src + ")", font=fr,
               fill=(120, 120, 120), anchor="lm")


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # ---- masthead ----
    d.text((W // 2, 40), "THE WORLD TODAY", font=font(SERIF_B, 60),
           fill=INK, anchor="mm")
    d.text((16, 40), "WORLD EDITION", font=font(SANS_B, 11), fill=INK,
           anchor="lm")
    d.text((W - 16, 40), "No. 325", font=font(SANS_B, 11), fill=INK,
           anchor="rm")
    d.line([14, 78, 1010, 78], fill=INK, width=2)
    d.line([14, 82, 1010, 82], fill=INK, width=1)
    d.text((16, 94), "SATURDAY, 21 NOVEMBER 2026",
           font=font(SERIF_B, 14), fill=INK, anchor="lm")
    d.text((W - 16, 94),
           "35 STORIES  ·  7 REGIONS  ·  EVERY ONE DATED SATURDAY 21 NOVEMBER 2026",
           font=font(SANS_B, 13), fill=RED, anchor="rm")
    d.text((W // 2, 112),
           "Iran strikes US bases in Bahrain · COP31 runs past its deadline "
           "· Strong quake shakes Peru",
           font=font(SERIF_I, 13), fill=(60, 60, 60), anchor="mm")
    d.line([14, 124, 1010, 124], fill=INK, width=1)

    # ---- stat strip: six big numbers ----
    cell_w = 166
    for i, (num, label) in enumerate(STATS):
        cx = 14 + i * cell_w + cell_w // 2
        d.text((cx, 146), num, font=font(SERIF_B, 26), fill=INK,
               anchor="mm")
        lines = wrap(d, label, font(SANS, 9), cell_w - 10)
        assert len(lines) <= 2, f"stat label too long: {label}"
        ly = 164
        for line in lines:
            d.text((cx, ly), line, font=font(SANS, 9), fill=(60, 60, 60),
                   anchor="mm")
            ly += 11
        if i < 5:
            x = 14 + (i + 1) * cell_w
            d.line([x, 132, x, 180], fill=(200, 195, 180), width=1)

    # ---- region bar: story counts per region ----
    seg_w = 994 // 7
    for i, (name, count, color) in enumerate(REGIONS):
        x0 = 14 + i * seg_w
        d.rectangle([x0, 188, x0 + seg_w - 1, 208], fill=color)
        d.text((x0 + seg_w // 2, 198), f"{name} {count}",
               font=font(SANS_B, 10), fill=(255, 255, 255), anchor="mm")

    # ---- three big panels ----
    pw, ph, gap = 326, 224, 9
    for i, panel in enumerate(PANELS):
        draw_panel(d, 14 + i * (pw + gap), 214, pw, ph, panel)

    # ---- ten medium cards, 5 x 2 ----
    mw, mh = 192, 120
    for i, med in enumerate(MEDIUM):
        col, row = i % 5, i // 5
        draw_medium(img, 14 + col * (mw + 9), 444 + row * 126, mw, mh, med)

    # ---- where it happened: map + numbered list ----
    d.text((16, 706), "WHERE IT HAPPENED", font=font(SERIF_B, 16),
           fill=INK, anchor="lm")
    d.text((W - 16, 706), "STORIES 14–35 · ALL DATED 21 NOV 2026",
           font=font(SANS_B, 10), fill=(90, 90, 90), anchor="rm")
    d.line([14, 718, 1010, 718], fill=INK, width=1)
    draw_map(d, 14, 724, 290, 130)
    d.text((14, 862), "Pins show where stories 14–35 happened.",
           font=font(SANS, 9), fill=(90, 90, 90), anchor="lm")
    draw_list(d, 316, 724, 343, LISTED[:11])
    draw_list(d, 663, 724, 343, LISTED[11:])

    # ---- date check ----
    d.rectangle([14, 910, 1010, 960], outline=RED, width=2)
    dc_body = ("Left out as Friday 20 November's news: the US stock "
               "market's fall into correction and the missile that landed "
               "in Poland. Not confirmed when drawn, so not shown: "
               "BepiColombo's Mercury orbit. Every story here happened, or "
               "was first reported, on Saturday 21 November 2026.")
    prefix = "DATE CHECK — "
    pf = font(SANS_B, 11)
    bf = font(SANS, 11)
    pw_px = int(d.textlength(prefix, font=pf))
    words = dc_body.split()
    lines = []
    avail = 1010 - 14 - 24 - pw_px
    cur, idx = "", 0
    while idx < len(words):
        trial = (cur + " " + words[idx]).strip()
        if d.textlength(trial, font=bf) <= avail:
            cur = trial
            idx += 1
        else:
            break
    lines.append(cur)
    cur = ""
    for w_ in words[idx:]:
        trial = (cur + " " + w_).strip()
        if d.textlength(trial, font=bf) <= 972:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    assert len(lines) <= 3, f"date check too long: {len(lines)} lines"
    y = 922
    d.text((26, y), prefix, font=pf, fill=RED, anchor="lm")
    d.text((26 + pw_px, y), lines[0], font=bf, fill=INK, anchor="lm")
    for line in lines[1:]:
        y += 14
        d.text((26, y), line, font=bf, fill=INK, anchor="lm")

    # ---- footer ----
    d.line([14, 974, 1010, 974], fill=INK, width=1)
    d.text((16, 987), "THE WORLD TODAY", font=font(SANS_B, 11), fill=INK,
           anchor="lm")
    d.text((W // 2, 987), "Compiled from major wire reports · 21 November 2026",
           font=font(SANS, 10), fill=(90, 90, 90), anchor="mm")
    d.text((W - 16, 987), "PAGE 1 OF 1", font=font(SANS_B, 11), fill=INK,
           anchor="rm")

    img.save("news.png", optimize=True)
    print("wrote news.png")


if __name__ == "__main__":
    main()
