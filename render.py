#!/usr/bin/env python3
"""THE ATLAS LEDGER v2 -- render the broadsheet for Tuesday 24 Nov 2026.

Build tool for the make.fun news-image-20261124 v2 entry. Run in the
build session (needs Pillow + the system fonts below); it is NOT run
by the entry itself -- main.py only copies the finished entry.png.
Every story drawn here is sourced in SOURCES.md, reported on
Tuesday 24 November 2026 (UTC).

    python3 render.py            # writes entry.png beside this file

Layout (1024x1024, winners' formula from news-image-20261122):
masthead (paper name + kicker + giant serif date + story-count
badge + red italic sub-headline) / UTC timeline strip / Day in
Numbers / region chips / 3 hero stories with flat illustrations /
grid of 10 / numbered list 14-36 / dotted world map with pins /
DATE CHECK footer. Character: ATLAS keeps the ledger.
"""
import hashlib
import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (244, 235, 211)
INK = (27, 52, 66)
INK_SOFT = (58, 82, 94)
RED = (178, 52, 38)
RED_SOFT = (196, 84, 62)
MUTED = (107, 98, 82)
FAINT = (201, 191, 166)
WHITE = (250, 248, 240)
NAVY_BAND = (27, 52, 66)
GREEN = (46, 125, 50)
SKY = (35, 80, 100)
GOLD = (198, 142, 32)

FONT_DIR = "/usr/share/fonts/truetype"
F_DATE = os.path.join(FONT_DIR, "noto", "NotoSerifDisplay-Black.ttf")
F_SERIF_B = os.path.join(FONT_DIR, "noto", "NotoSerif-Bold.ttf")
F_SERIF_I = os.path.join(FONT_DIR, "noto", "NotoSerif-Italic.ttf")
F_SANS_B = os.path.join(FONT_DIR, "dejavu", "DejaVuSans-Bold.ttf")
F_SANS = os.path.join(FONT_DIR, "dejavu", "DejaVuSans.ttf")

_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines fitting max_w."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_tracked(draw, cx, y, text, fnt, fill, tracking=2):
    """Centred text with extra letter spacing."""
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + tracking
    return total


def draw_centered(draw, cx, y, text, fnt, fill):
    draw.text((cx - draw.textlength(text, font=fnt) / 2, y), text,
              font=fnt, fill=fill)


def hline(draw, x0, x1, y, fill, thick=1):
    draw.rectangle([x0, y, x1, y + thick - 1], fill=fill)


def rrect(draw, box, fill=None, outline=None, width=1, radius=6):
    draw.rounded_rectangle(box, radius=radius, fill=fill,
                           outline=outline, width=width)


def badge(draw, x, y, text, fnt, bg, fg=WHITE):
    """Small pill badge; returns its width."""
    pad = 7
    w = draw.textlength(text, font=fnt) + pad * 2
    h = fnt.size + 8
    draw.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=bg)
    draw.text((x + pad, y + 4), text, font=fnt, fill=fg)
    return w

# ------------------------------------------------------------------ data
# (headline, summary, source, status) -- every fact sourced in
# SOURCES.md, reported Tuesday 24 November 2026 (UTC).
HEROES = [
    ("HUANG IS BACK",
     "Nvidia +31% in a day as Trump restores Huang; Nasdaq +6.5%.",
     "REUTERS", "REPORTED"),
    ("ZAPORIZHZHIA HIT",
     "Overnight Russian strike hits an apartment block: 2 dead, "
     "40 hurt.",
     "GOV. SEMIKIN", "REPORTED"),
    ("GAZA: HAMAS SECURITY CHIEF KILLED",
     "Israeli strike kills Naeem Abu Nahel, Hamas security chief, "
     "and six others.",
     "MEDICS / POLICE", "REPORTED"),
]

GRID = [
    ("COP31: THE FLOP",
     "No deal in Antalya; first COP since 2009 without a pact.",
     "REUTERS"),
    ("NUKE IN SPACE?",
     "Allies warn of a Russian nuclear satellite in space.",
     "NATO / ALLIES"),
    ("ESTONIA ON EDGE",
     "Russia: Estonia is 'on verge of triggering open war'.",
     "MOSCOW"),
    ("LIBYA FALLOUT",
     "Kyiv: ship strike was self-defence; UN seeks a probe.",
     "KYIV / UN"),
    ("GERMANY GETS DELTA",
     "Berlin first to access Ukraine's Delta system.",
     "BERLIN"),
    ("DHAKA PAY PROTESTS",
     "Garment workers clash with police; factories shut.",
     "DHAKA"),
    ("SOLOMONS CUT CHINA",
     "Solomon Islands to end its security pact with China.",
     "HONIARA"),
    ("ROHINGYA RULING BACKED",
     "14 nations recognise the ICJ decision on Myanmar.",
     "LONDON ET AL."),
    ("SPACEX SUED",
     "Oregon and Virginia sue SpaceX over Grok images.",
     "OREGON / VIRGINIA"),
    ("NEPAL QUAKE",
     "Magnitude 5.6 quake strikes Nepal near China border.",
     "KATHMANDU"),
]

# (number, headline, source) -- one line each, stories 14-36.
LISTED = [
    (14, "NETANYAHU PUSHES TRUMP TO RESUME IRAN STRIKES", "TEL AVIV"),
    (15, "IRAN: NO TALKS UNTIL US MEETS 7 TERMS", "TEHRAN"),
    (16, "HORMUZ LOG: RECORD IRANIAN ATTACKS IN STRAIT", "LONDON"),
    (17, "NORWAY'S DRONE PACT WITH KYIV EXPANDS", "OSLO"),
    (18, "RUTTE MEETS TRUMP WEDNESDAY IN FLORIDA", "WASHINGTON"),
    (19, "LATVIA: WAR MAY REACH TIPPING POINT NEXT YEAR", "NEW YORK"),
    (20, "GERMANS TURN: 53% NOW OPPOSE UKRAINE AID", "BERLIN"),
    (21, "SEOUL'S AI BOUNTY: $375,000 TO CATCH EXAM CHEATS", "SEOUL"),
    (22, "TAIWAN VOTES SATURDAY; BEIJING WATCHES", "TAIPEI"),
    (23, "BRITAIN'S HEAT TOLL: RECORD 5,258 DEAD IN 2026", "LONDON"),
    (24, "MEASLES IN PENNSYLVANIA: NINTH DEATH", "HARRISBURG"),
    (25, "EBOLA TRAPPED: FIGHTING IN ITURI, DRC", "GOMA"),
    (26, "IRAQ'S OIL ORDER: BAGHDAD TAKES KURD FIELDS", "BAGHDAD"),
    (27, "TIANGONG'S GUEST: FIRST FOREIGN ASTRONAUT", "BEIJING"),
    (28, "COLOMBIA CAR BOMB WRECKS VILLAVICENCIO", "BOGOTA"),
    (29, "YEMEN STRIKES: HOUTHIS REPORT DOZENS DEAD", "SANAA"),
    (30, "CIKANDE FIRE TOLL: 24 DEAD, ~30 MISSING", "JAKARTA"),
    (31, "OXFAM: GAZA 'TRANSFORMED INTO A TOXIC LAND'", "GAZA"),
    (32, "UK SANCTIONS MYANMAR GENERALS", "LONDON"),
    (33, "BURNHAM: NO EU RETURN WITHOUT REFERENDUM", "MANCHESTER"),
    (34, "ARM KEEPS HAAS AS CEO TO 2033", "CAMBRIDGE"),
    (35, "FOOD AID WARNING: WARS HIT 7.3M MORE PEOPLE", "ROME"),
    (36, "LEAKED DATA REVEALS SCALE OF RUSSIAN DEATHS", "KYIV"),
]

NUMBERS = [
    ("+6.5%", "NASDAQ, TUESDAY"),
    ("40", "HURT IN ZAPORIZHZHIA"),
    ("5,258", "UK HEAT DEATHS, 2026"),
    ("$375,000", "AI-CHEAT REWARD, KOREA"),
    ("14", "NATIONS BACK ICJ RULING"),
    ("5.6", "NEPAL QUAKE MAGNITUDE"),
]

TIMELINE = [
    ("03:48", "TRUMP TO MEET RUTTE WED."),
    ("MORNING", "SEOUL +6%, NIKKEI +3.9%"),
    ("MIDDAY", "ZAPORIZHZHIA: 2 DEAD"),
    ("AFTERNOON", "GAZA CHIEF KILLED"),
    ("EVENING", "DELTA SIGNED, BERLIN"),
]

REGIONS = [("EUROPE", 11), ("MIDDLE EAST", 7), ("ASIA", 6),
           ("AMERICAS", 5), ("AFRICA", 2), ("SOUTH ASIA", 2),
           ("WORLD", 2), ("OCEANIA", 1)]

SUBHEAD_LINES = [
    "Huang is back \u2014 Nasdaq +6.5%  \u00b7  Zaporizhzhia hit "
    "overnight, 2 dead, 40 hurt",
    "Israel kills Hamas security chief in Gaza",
]

# Stylised world map: continents as (lon, lat, rx, ry) ellipses.
LAND = [
    (-100, 48, 52, 22), (-88, 22, 18, 10), (-102, 66, 38, 12),
    (-42, 72, 12, 7), (-60, -12, 17, 26), (-66, -34, 8, 11),
    (14, 52, 21, 11), (-2, 54, 4, 5), (18, 4, 21, 26),
    (20, -20, 14, 13), (45, 26, 17, 11), (80, 50, 54, 20),
    (100, 26, 28, 16), (78, 20, 11, 11), (105, 10, 14, 9),
    (115, -2, 17, 5), (134, -25, 17, 9), (172, -41, 5, 6),
    (140, 40, 14, 9), (105, 35, 24, 13),
]

# (lon, lat) of the 13 main stories, in story order.
PINS = [(-122, 38), (35, 48), (34, 32), (31, 37), (38, 56),
        (25, 59), (20, 32), (13, 53), (90, 24), (160, -9),
        (96, 21), (-98, 30), (85, 28)]

# ------------------------------------------------------------- artwork
def hero_chip(draw, x, y, w, h):
    """Flat vector: a chip on a navy board, green arrow climbing."""
    draw.rectangle([x, y, x + w, y + h], fill=(23, 42, 54))
    draw.rectangle([x, y, x + w, y + 5], fill=RED)
    # chip body, right side
    cx, cy = x + w - 78, y + h // 2
    draw.rectangle([cx - 26, cy - 26, cx + 26, cy + 26], fill=(242, 235, 211))
    for dx in (-34, -17, 0, 17, 34):
        draw.rectangle([cx + dx - 2, cy - 36, cx + dx + 2, cy - 26],
                       fill=(242, 235, 211))
        draw.rectangle([cx + dx - 2, cy + 26, cx + dx + 2, cy + 36],
                       fill=(242, 235, 211))
    draw.text((cx - 14, cy - 13), "AI", font=font(F_SANS_B, 24),
              fill=(23, 42, 54))
    # rising arrow, lower right, clear of the +31% label
    pts = [(x + 96, y + h - 16), (x + 130, y + h - 38),
           (x + 158, y + h - 30), (x + 196, y + h - 56)]
    draw.line(pts, fill=(110, 200, 90), width=5, joint="curve")
    draw.polygon([(x + 196, y + h - 56), (x + 178, y + h - 54),
                  (x + 194, y + h - 38)], fill=(110, 200, 90))
    draw.text((x + 14, y + h - 36), "+31%", font=font(F_SANS_B, 26),
              fill=(110, 200, 90))


def hero_zaporizhzhia(draw, x, y, w, h):
    """Flat vector: night skyline, one building hit, smoke, drone."""
    draw.rectangle([x, y, x + w, y + h], fill=(31, 48, 66))
    for i in range(14):
        sx = x + 8 + i * 23
        sy = y + 8 + (i * 7) % 14
        draw.ellipse([sx, sy, sx + 2, sy + 2], fill=(180, 190, 200))
    # buildings
    for bx, bw, bh in ((14, 52, 58), (74, 44, 74), (126, 58, 48),
                       (192, 46, 66), (246, 54, 56)):
        draw.rectangle([x + bx, y + h - bh, x + bx + bw, y + h],
                       fill=(16, 28, 38))
        for wy in range(y + h - bh + 8, y + h - 6, 12):
            for wx in range(x + bx + 7, x + bx + bw - 7, 12):
                if (wx + wy) % 3:
                    draw.rectangle([wx, wy, wx + 4, wy + 5],
                                   fill=(240, 200, 90))
    # blast on the middle tower: spiky starburst, no yellow core
    bx, by = x + 96, y + h - 52
    star = []
    for k in range(12):
        ang = math.pi * k / 6
        r = 17 if k % 2 == 0 else 8
        star.append((bx + r * math.cos(ang), by + r * math.sin(ang)))
    draw.polygon(star, fill=(232, 90, 30))
    draw.ellipse([bx - 7, by - 7, bx + 7, by + 7], fill=(178, 52, 38))
    # smoke
    for sx, sy, r in ((x + 132, y + 10, 11), (x + 150, y + 6, 8),
                      (x + 116, y + 16, 7)):
        draw.ellipse([sx - r, sy - r, sx + r, sy + r],
                     fill=(120, 125, 130))
    # drone silhouette
    dx, dy = x + w - 52, y + 16
    draw.polygon([(dx - 16, dy), (dx + 16, dy), (dx, dy + 8)],
                 fill=(10, 18, 26))
    draw.line([dx - 22, dy - 2, dx + 22, dy - 2], fill=(10, 18, 26),
              width=2)


def hero_gaza(draw, x, y, w, h):
    """Flat vector: dusk sky, skyline, smoke plume, red sun."""
    for i, col in enumerate(((214, 110, 60), (196, 84, 52),
                             (178, 62, 48))):
        draw.rectangle([x, y + i * h // 3, x + w, y + (i + 1) * h // 3],
                       fill=col)
    draw.ellipse([x + w - 62, y + 10, x + w - 22, y + 50],
                 fill=(250, 220, 150))
    # skyline
    for bx, bw, bh in ((10, 46, 44), (62, 38, 60), (106, 52, 38),
                       (164, 40, 54), (210, 48, 44), (264, 40, 58)):
        draw.rectangle([x + bx, y + h - bh, x + bx + bw, y + h],
                       fill=(52, 28, 30))
        for wy in range(y + h - bh + 7, y + h - 5, 11):
            for wx in range(x + bx + 6, x + bx + bw - 6, 11):
                if (wx * 7 + wy) % 4:
                    draw.rectangle([wx, wy, wx + 3, wy + 4],
                                   fill=(250, 220, 150))
    # smoke plume
    for sx, sy, r in ((x + 150, y + 22, 13), (x + 168, y + 12, 10),
                      (x + 132, y + 30, 9), (x + 182, y + 22, 8)):
        draw.ellipse([sx - r, sy - r, sx + r, sy + r],
                     fill=(70, 60, 60))
    # minaret
    draw.rectangle([x + 232, y + h - 78, x + 238, y + h], fill=(52, 28, 30))
    draw.polygon([(x + 230, y + h - 78), (x + 240, y + h - 78),
                  (x + 235, y + h - 90)], fill=(52, 28, 30))


HERO_ART = [hero_chip, hero_zaporizhzhia, hero_gaza]


def icon(draw, x, y, kind):
    """30x30 flat icon for a grid story, on a cream tile."""
    draw.rectangle([x, y, x + 30, y + 30], fill=(232, 222, 190))
    draw.rectangle([x, y, x + 30, y + 30], outline=INK, width=1)
    c = INK
    if kind == "globe":
        draw.ellipse([x + 5, y + 5, x + 25, y + 25], outline=c, width=2)
        draw.ellipse([x + 11, y + 5, x + 19, y + 25], outline=c, width=1)
        draw.line([x + 5, y + 15, x + 25, y + 15], fill=c, width=1)
    elif kind == "sat":
        draw.rectangle([x + 12, y + 12, x + 18, y + 18], fill=c)
        draw.rectangle([x + 4, y + 10, x + 10, y + 20], outline=c, width=1)
        draw.rectangle([x + 20, y + 10, x + 26, y + 20], outline=c, width=1)
        draw.line([x + 15, y + 18, x + 22, y + 25], fill=c, width=2)
    elif kind == "flag":
        draw.rectangle([x + 6, y + 5, x + 24, y + 11], fill=RED)
        draw.rectangle([x + 6, y + 11, x + 24, y + 17], fill=WHITE)
        draw.rectangle([x + 6, y + 17, x + 24, y + 23], fill=c)
        draw.line([x + 6, y + 5, x + 6, y + 26], fill=c, width=2)
    elif kind == "ship":
        draw.polygon([(x + 5, y + 18), (x + 25, y + 18), (x + 21, y + 24),
                      (x + 9, y + 24)], fill=c)
        draw.line([x + 15, y + 6, x + 15, y + 18], fill=c, width=2)
        draw.polygon([(x + 15, y + 7), (x + 23, y + 14), (x + 15, y + 14)],
                     fill=RED)
        draw.line([x + 4, y + 27, x + 26, y + 27], fill=c, width=1)
    elif kind == "shield":
        draw.polygon([(x + 15, y + 5), (x + 24, y + 8), (x + 24, y + 16),
                      (x + 15, y + 25), (x + 6, y + 16), (x + 6, y + 8)],
                     outline=c, width=2)
        draw.line([x + 10, y + 15, x + 14, y + 19], fill=RED, width=2)
        draw.line([x + 14, y + 19, x + 21, y + 11], fill=RED, width=2)
    elif kind == "factory":
        draw.rectangle([x + 5, y + 14, x + 19, y + 25], fill=c)
        draw.rectangle([x + 20, y + 18, x + 26, y + 25], fill=c)
        draw.rectangle([x + 7, y + 5, x + 10, y + 14], fill=c)
        draw.ellipse([x + 12, y + 4, x + 17, y + 9], fill=MUTED)
    elif kind == "island":
        draw.ellipse([x + 4, y + 17, x + 26, y + 24], fill=(198, 164, 90))
        draw.line([x + 15, y + 8, x + 15, y + 18], fill=c, width=2)
        draw.polygon([(x + 15, y + 8), (x + 23, y + 11), (x + 15, y + 14)],
                     fill=RED)
        draw.line([x + 3, y + 26, x + 27, y + 26], fill=SKY, width=2)
    elif kind == "scales":
        draw.line([x + 15, y + 6, x + 15, y + 24], fill=c, width=2)
        draw.line([x + 7, y + 9, x + 23, y + 9], fill=c, width=2)
        draw.polygon([(x + 4, y + 16), (x + 10, y + 16), (x + 7, y + 11)],
                     outline=c, width=1)
        draw.polygon([(x + 20, y + 16), (x + 26, y + 16), (x + 23, y + 11)],
                     outline=c, width=1)
    elif kind == "rocket":
        draw.polygon([(x + 15, y + 4), (x + 20, y + 14), (x + 10, y + 14)],
                     fill=c)
        draw.rectangle([x + 11, y + 14, x + 19, y + 22], fill=RED)
        draw.polygon([(x + 13, y + 22), (x + 17, y + 22), (x + 15, y + 27)],
                     fill=GOLD)
    elif kind == "quake":
        draw.line([(x + 4, y + 8), (x + 10, y + 16), (x + 14, y + 10),
                   (x + 20, y + 20), (x + 26, y + 12)], fill=RED, width=2)
        draw.rectangle([x + 5, y + 20, x + 11, y + 26], outline=c, width=1)
        draw.rectangle([x + 18, y + 20, x + 25, y + 26], outline=c, width=1)


ICONS = ["globe", "sat", "flag", "ship", "shield", "factory",
         "island", "scales", "rocket", "quake"]

# -------------------------------------------------------------- compose
def compose():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead -------------------------------------------------
    draw_tracked(d, W // 2, 10, "THE ATLAS LEDGER \u00b7 KEPT BY ATLAS",
                 font(F_SANS_B, 12), INK_SOFT, tracking=3)
    draw_tracked(d, W // 2, 32, "THE WORLD IN ONE DAY",
                 font(F_SANS_B, 23), INK, tracking=5)
    size = 66
    while (d.textlength("Tuesday 24 November 2026",
                        font=font(F_DATE, size)) > 976 and size > 40):
        size -= 2
    draw_centered(d, W // 2, 58, "Tuesday 24 November 2026",
                  font(F_DATE, size), INK)
    # story-count badge line: numbers in red, words in navy
    y = 132
    parts = [("36", RED), (" STORIES \u00b7 ", INK), ("8", RED),
             (" REGIONS \u00b7 ALL FROM THIS ONE DAY", INK)]
    f_badge = font(F_SANS_B, 17)
    total = sum(d.textlength(t, font=f_badge) for t, _ in parts)
    x = (W - total) / 2
    for text, col in parts:
        d.text((x, y), text, font=f_badge, fill=col)
        x += d.textlength(text, font=f_badge)
    # red italic sub-headline, two set lines
    f_sub = font(F_SERIF_I, 19)
    yy = 158
    for line in SUBHEAD_LINES:
        draw_centered(d, W // 2, yy, line, f_sub, RED)
        yy += 25
    hline(d, 24, 1000, 210, INK, thick=2)

    # ---- timeline strip (one line per column) ---------------------
    col_w = (976 - 4 * 12) / 5
    for i, (when, what) in enumerate(TIMELINE):
        cx = 24 + i * (col_w + 12) + col_w / 2
        draw_centered(d, cx, 218, when, font(F_SANS_B, 11), RED)
        short = what
        while (d.textlength(short, font=font(F_SANS, 11)) > col_w
               and len(short) > 8):
            short = short[:-2]
        if short != what:
            short = short.rstrip() + "\u2026"
        draw_centered(d, cx, 234, short, font(F_SANS, 11), INK)
    hline(d, 24, 1000, 256, FAINT)

    # ---- the day in numbers ---------------------------------------
    draw_tracked(d, W // 2, 264, "THE DAY IN NUMBERS",
                 font(F_SANS_B, 12), INK, tracking=3)
    bw = (976 - 5 * 12) / 6
    for i, (num, label) in enumerate(NUMBERS):
        cx = 24 + i * (bw + 12) + bw / 2
        draw_centered(d, cx, 282, num, font(F_SERIF_B, 25), INK)
        short = label
        while (d.textlength(short, font=font(F_SANS, 10)) > bw
               and len(short) > 8):
            short = short[:-2]
        if short != label:
            short = short.rstrip() + "\u2026"
        draw_centered(d, cx, 312, short, font(F_SANS, 10), MUTED)
    # ---- region chips ----------------------------------------------
    f_chip = font(F_SANS_B, 12)
    chips = []
    for name, n in REGIONS:
        w = d.textlength(f"{name} {n}", font=f_chip) + 18
        chips.append((name, n, w))
    total = sum(w for _, _, w in chips) + 8 * (len(chips) - 1)
    x = (W - total) / 2
    y = 330
    for name, n, w in chips:
        rrect(d, [x, y, x + w, y + 24], outline=INK, width=1, radius=12)
        tx = x + 9
        d.text((tx, y + 5), name, font=f_chip, fill=INK)
        tx += d.textlength(name, font=f_chip) + 4
        d.text((tx, y + 5), str(n), font=f_chip, fill=RED)
        x += w + 8
    hline(d, 24, 1000, 362, INK, thick=1)

    # ---- hero stories ---------------------------------------------
    hx = [24, 352, 680]
    hw = 320
    for i, (head, summ, src, status) in enumerate(HEROES):
        x = hx[i]
        HERO_ART[i](d, x, 370, hw, 72)
        badge(d, x + 8, 376, status, font(F_SANS_B, 10), RED)
        y = 450
        for line in wrap(d, head, font(F_SANS_B, 17), hw)[:2]:
            d.text((x, y), line, font=font(F_SANS_B, 17), fill=INK)
            y += 21
        for line in wrap(d, summ, font(F_SANS, 12), hw)[:2]:
            d.text((x, y), line, font=font(F_SANS, 12), fill=INK_SOFT)
            y += 15
        d.text((x, y + 2), f"SOURCE: {src}", font=font(F_SANS, 10),
               fill=MUTED)
    hline(d, 24, 1000, 538, FAINT)

    # ---- grid of 10 ------------------------------------------------
    gw = (976 - 4 * 8) / 5
    gh = 64
    for i, (head, summ, src) in enumerate(GRID):
        row, col = divmod(i, 5)
        x = 24 + col * (gw + 8)
        y = 546 + row * (gh + 4)
        icon(d, x, y + 2, ICONS[i])
        tx = x + 36
        tw = gw - 36
        yy = y + 1
        for line in wrap(d, head, font(F_SANS_B, 12), tw)[:2]:
            d.text((tx, yy), line, font=font(F_SANS_B, 12), fill=INK)
            yy += 15
        yy = y + 34
        for line in wrap(d, summ, font(F_SANS, 11), gw)[:2]:
            d.text((x, yy), line, font=font(F_SANS, 11), fill=INK_SOFT)
            yy += 13
        if col < 4:
            d.line([x + gw + 4, y + 2, x + gw + 4, y + gh - 2], fill=FAINT)
    hline(d, 24, 1000, 684, INK, thick=1)

    # ---- numbered list 14-36 ---------------------------------------
    d.text((24, 692), "ALSO ON TUESDAY 24 NOVEMBER \u2014 23 MORE STORIES",
           font=font(F_SANS_B, 12), fill=INK)
    f_num = font(F_SANS_B, 12)
    f_head = font(F_SANS_B, 12)
    f_src = font(F_SANS, 11)
    for k, (num, head, src) in enumerate(LISTED):
        col = 0 if k < 12 else 1
        row = k if k < 12 else k - 12
        x = 24 if col == 0 else 524
        y = 712 + row * 14
        d.text((x, y), f"{num}", font=f_num, fill=RED)
        hx2 = x + 26
        max_w = 476 - 26 - d.textlength(f" \u2014 {src}", font=f_src) - 4
        shown = head
        while d.textlength(shown, font=f_head) > max_w and len(shown) > 8:
            shown = shown[:-2]
        if shown != head:
            shown = shown.rstrip() + "\u2026"
        d.text((hx2, y), shown, font=f_head, fill=INK)
        d.text((hx2 + d.textlength(shown, font=f_head), y),
               f" \u2014 {src}", font=f_src, fill=MUTED)
    hline(d, 24, 1000, 884, FAINT)

    # ---- dotted world map ------------------------------------------
    d.text((24, 892), "WHERE IT HAPPENED \u2014 STYLISED MAP",
           font=font(F_SANS_B, 11), fill=INK)
    map_x0, map_y0, map_w, map_h = 24, 908, 976, 52

    def to_xy(lon, lat):
        return (map_x0 + (lon + 170) / 360 * map_w,
                map_y0 + (75 - lat) / 130 * map_h)

    step = 6
    gx = map_x0
    while gx <= map_x0 + map_w:
        gy = map_y0
        while gy <= map_y0 + map_h:
            lon = (gx - map_x0) / map_w * 360 - 170
            lat = 75 - (gy - map_y0) / map_h * 130
            on_land = any(((lon - cl) / rx) ** 2 + ((lat - ct) / ry) ** 2
                          <= 1 for cl, ct, rx, ry in LAND)
            if on_land:
                d.ellipse([gx - 1, gy - 1, gx + 1, gy + 1], fill=INK_SOFT)
            gy += step
        gx += step
    # pins: small dot on the true spot; the Europe / Middle East
    # cluster gets a numbered badge nudged aside with a leader line
    PIN_SHIFT = {2: (16, -2), 3: (0, 14), 4: (18, 4), 5: (18, -8),
                 6: (-8, -4), 7: (-16, 10), 8: (-18, -6)}
    for n, (lon, lat) in enumerate(PINS, start=1):
        px, py = to_xy(lon, lat)
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=RED)
        bx, by = px, py
        if n in PIN_SHIFT:
            dx, dy = PIN_SHIFT[n]
            bx, by = px + dx, py + dy
            d.line([px, py, bx, by], fill=RED, width=1)
        d.ellipse([bx - 6, by - 6, bx + 6, by + 6], fill=RED,
                  outline=WHITE, width=1)
        num = str(n)
        d.text((bx - d.textlength(num, font=font(F_SANS_B, 8)) / 2, by - 5),
               num, font=font(F_SANS_B, 8), fill=WHITE)

    # ---- date check footer -----------------------------------------
    d.rectangle([24, 966, 1000, 1014], fill=NAVY_BAND)
    draw_centered(d, W // 2, 974,
                  "DATE CHECK \u2014 Every story here happened, or was "
                  "first reported, on Tuesday 24 November 2026 (UTC).",
                  font(F_SANS_B, 12), WHITE)
    draw_centered(d, W // 2, 994,
                  "HOW SURE: REPORTED = carried by the wires  \u00b7  "
                  "CLAIM = one side's account  \u00b7  ONGOING = still "
                  "unfolding  \u00b7  THE ATLAS LEDGER \u00b7 KEPT BY ATLAS",
                  font(F_SANS, 10), (210, 220, 228))
    return img


def main():
    img = compose()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img.save(out, optimize=True)
    data = open(out, "rb").read()
    print("wrote %s %d bytes sha256=%s"
          % (out, len(data), hashlib.sha256(data).hexdigest()))
    thumb = img.resize((300, 300), Image.LANCZOS)
    thumb.save(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "entry-300.png"), optimize=True)
    print("thumbnail entry-300.png written for the legibility check")


if __name__ == "__main__":
    main()
