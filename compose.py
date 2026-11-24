#!/usr/bin/env python3
"""THE FIRST LIGHT POST — NI23 G4 entry composer for akun4 (@pcrypto012).

A one-page broadsheet front page for Monday 23 November 2026, drawn with PIL
in the fleet's lead()/mini()/grid style. Palette: light grey paper, black
ink, burnt-orange accent. Two layouts (A and B) are rendered from the same
locked pool content so a duel can pick the stronger page; the winner is
saved as entry.png. Local build only.
"""
import math
import sys
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = "/home/hatch/workspace/tools/bedah-19nov/news-image/fonts/"
W = H = 1024
PAPER = (233, 230, 224)
PANEL = (250, 248, 243)
INK = (18, 17, 15)
MUTE = (92, 88, 80)
ACCENT = (194, 81, 31)  # burnt orange
RULE = (40, 38, 34)

REGION_COLORS = {
    "MIDDLE EAST": (179, 64, 30),
    "EUROPE": (36, 86, 166),
    "NORTH AMERICA": (106, 63, 160),
    "SOUTH ASIA": (30, 122, 76),
    "ASIA-PACIFIC": (14, 124, 134),
    "AFRICA": (166, 124, 26),
    "GLOBAL": (85, 80, 73),
}
STATUS_COLORS = {
    "REPORTED": (36, 86, 166),
    "CLAIM": (179, 64, 30),
    "ONGOING": (150, 105, 10),
    "OFFICIAL": (30, 122, 76),
    "ON RECORD": (106, 63, 160),
}

_cache = {}


def F(name, size):
    key = (name, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(FONT_DIR + name, size)
    return _cache[key]


def fb(size):
    """Headline font (bold)."""
    return F("Archivo-Bold.ttf", size)


def fr(size):
    """Deck font (regular)."""
    return F("Archivo.ttf", size)


def fsr(size):
    """Brief font (regular, small)."""
    return F("Archivo.ttf", size)


def tw(d, text, font):
    return d.textlength(text, font=font)


def wrap(d, text, font, maxw, max_lines=None):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if tw(d, trial, font) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and tw(d, lines[-1] + "…", font) > maxw and len(lines[-1]) > 1:
            lines[-1] = lines[-1][:-1]
        lines[-1] += "…"
    return lines


# ---------------------------------------------------------------- icons
def icon(d, kind, x, y, s, col):
    """Tiny flat original pictograms, drawn with primitives only."""
    if kind == "ship":
        d.polygon([(x, y + s * .62), (x + s, y + s * .62), (x + s * .82, y + s * .85), (x + s * .18, y + s * .85)], fill=col)
        d.rectangle([x + s * .42, y + s * .18, x + s * .58, y + s * .62], fill=col)
        d.line([x + s * .1, y + s * .95, x + s * .9, y + s * .95], fill=col, width=2)
    elif kind == "flame":
        d.polygon([(x + s * .5, y), (x + s * .85, y + s * .6), (x + s * .7, y + s), (x + s * .3, y + s), (x + s * .15, y + s * .6)], fill=col)
        d.ellipse([x + s * .38, y + s * .55, x + s * .62, y + s * .95], fill=(250, 200, 90))
    elif kind == "radar":
        d.polygon([(x + s * .5, y + s), (x + s * .3, y + s * .35), (x + s * .7, y + s * .35)], outline=col, width=3)
        d.arc([x + s * .15, y, x + s * .85, y + s * .6], 200, 340, fill=col, width=3)
        d.ellipse([x + s * .44, y + s * .3, x + s * .56, y + s * .42], fill=col)
    elif kind == "rubble":
        d.polygon([(x, y + s), (x + s * .3, y + s * .3), (x + s * .55, y + s * .55), (x + s * .8, y + s * .2), (x + s, y + s)], fill=col)
        d.rectangle([x + s * .08, y + s * .45, x + s * .3, y + s * .7], outline=col, width=3)
    elif kind == "globe":
        d.ellipse([x + s * .08, y + s * .08, x + s * .92, y + s * .92], outline=col, width=3)
        d.line([x + s * .08, y + s * .5, x + s * .92, y + s * .5], fill=col, width=2)
        d.line([x + s * .5, y + s * .08, x + s * .5, y + s * .92], fill=col, width=2)
    elif kind == "capitol":
        d.polygon([(x + s * .5, y + s * .05), (x + s * .95, y + s * .35), (x + s * .05, y + s * .35)], fill=col)
        for i in range(4):
            cx = x + s * (.16 + i * .22)
            d.rectangle([cx, y + s * .45, cx + s * .08, y + s * .8], fill=col)
        d.rectangle([x + s * .05, y + s * .85, x + s * .95, y + s * .95], fill=col)
    elif kind == "robot":
        d.rectangle([x + s * .2, y + s * .3, x + s * .8, y + s * .85], outline=col, width=3)
        d.ellipse([x + s * .33, y + s * .48, x + s * .45, y + s * .6], fill=col)
        d.ellipse([x + s * .55, y + s * .48, x + s * .67, y + s * .6], fill=col)
        d.line([x + s * .5, y + s * .3, x + s * .5, y + s * .1], fill=col, width=3)
    elif kind == "cricket":
        d.polygon([(x + s * .55, y), (x + s * .8, y + s * .1), (x + s * .35, y + s * .8), (x + s * .15, y + s * .7)], fill=col)
        d.ellipse([x + s * .6, y + s * .68, x + s * .92, y + s], fill=(179, 40, 40))
    elif kind == "scales":
        d.line([x + s * .5, y + s * .1, x + s * .5, y + s * .85], fill=col, width=3)
        d.line([x + s * .12, y + s * .25, x + s * .88, y + s * .25], fill=col, width=3)
        d.polygon([(x + s * .12, y + s * .25), (x, y + s * .55), (x + s * .24, y + s * .55)], outline=col, width=2)
        d.polygon([(x + s * .88, y + s * .25), (x + s * .76, y + s * .55), (x + s, y + s * .55)], outline=col, width=2)
        d.rectangle([x + s * .3, y + s * .88, x + s * .7, y + s * .97], fill=col)
    elif kind == "drone":
        d.line([x + s * .2, y + s * .2, x + s * .8, y + s * .8], fill=col, width=3)
        d.line([x + s * .8, y + s * .2, x + s * .2, y + s * .8], fill=col, width=3)
        for cx, cy in [(.2, .2), (.8, .2), (.2, .8), (.8, .8)]:
            d.ellipse([x + s * (cx - .13), y + s * (cy - .13), x + s * (cx + .13), y + s * (cy + .13)], outline=col, width=2)
        d.ellipse([x + s * .42, y + s * .42, x + s * .58, y + s * .58], fill=col)
    elif kind == "burst":
        for a in range(0, 360, 45):
            ex = x + s * .5 + s * .48 * math.cos(math.radians(a))
            ey = y + s * .5 + s * .48 * math.sin(math.radians(a))
            d.line([x + s * .5, y + s * .5, ex, ey], fill=col, width=3)
        d.ellipse([x + s * .35, y + s * .35, x + s * .65, y + s * .65], fill=col)
    elif kind == "gold":
        d.polygon([(x + s * .1, y + s * .55), (x + s * .35, y + s * .35), (x + s * .65, y + s * .35), (x + s * .9, y + s * .55), (x + s * .8, y + s * .8), (x + s * .2, y + s * .8)], fill=col)
        d.polygon([(x + s * .25, y + s * .3), (x + s * .45, y + s * .12), (x + s * .6, y + s * .12), (x + s * .75, y + s * .3), (x + s * .68, y + s * .45), (x + s * .32, y + s * .45)], fill=col)


# ---------------------------------------------------------------- content
# grid cards 4-12: (num, region, "LOC|CAT|STATUS", src, head, deck, kind)
grid = [
    (4, "EUROPE", "ANTALYA, TÜRKIYE|CLIMATE|OFFICIAL", "BBC / AP",
     "COP31 ends, no deal",
     "Summit closes in Antalya; the Turkish draft omits 'fossil fuels'.", "globe"),
    (5, "EUROPE", "GULF OF FINLAND|WAR|ONGOING", "BBC News",
     "Ship burns off Finland",
     "The Russian cargo ship was still burning off Finland after an attack.", "ship"),
    (6, "NORTH AMERICA", "WASHINGTON, USA|POLITICS|REPORTED", "BBC News",
     "Democrats win the House",
     "Majority 258–173, largest since 1992.", "capitol"),
    (7, "GLOBAL", "UNITED NATIONS|TECHNOLOGY|OFFICIAL", "Salonvision wire",
     "UN keeps AI talks open",
     "Talks continue at the United Nations on lethal AI weapons.", "robot"),
    (8, "SOUTH ASIA", "WELLINGTON, NZ|SPORT|REPORTED", "Observer Voice",
     "India declare on 720/9",
     "A record Test total on New Zealand soil, made at Wellington.", "cricket"),
    (9, "ASIA-PACIFIC", "THE HAGUE|LAW|OFFICIAL", "Guardian / NYT wire",
     "ICJ: Myanmar guilty",
     "Genocide of the Rohingya; 700,000+ fled the 2017 campaign.", "scales"),
    (10, "EUROPE", "KYIV REGION|WAR|ON RECORD", "Jagran Josh",
     "Kyiv: 14 missing, Zelenskiy says",
     "The Russian drone hit a Kyiv building.", "drone"),
    (11, "AFRICA", "BENGHAZI, LIBYA|WAR|REPORTED", "BBC News",
     "Suspected drone strike",
     "Blast on a Russian ship, Benghazi.", "burst"),
    (12, "GLOBAL", "WORLD MARKETS|MARKETS|REPORTED", "Observer Voice",
     "Gold slides to $3,538",
     "Down over $2,000 from the 2026 record of $5,595 an ounce.", "gold"),
]

NUMS = [
    ("258–173", "US HOUSE RESULT"),
    ("720/9", "INDIA TEST RECORD"),
    ("14", "MISSING NEAR KYIV"),
    ("$3,538", "GOLD PER OUNCE"),
    ("6", "KILLED IN KYIV"),
    ("65.9%", "INDIGO HOME SHARE"),
]

TL = [
    ("00:02Z", "UN: lethal-AI talks go on"),
    ("02:00Z", "Albanese on COP31"),
    ("MORNING", "COP31 ends, no deal"),
    ("MIDDAY", "Kyiv boy pulled alive"),
    ("EVENING", "Tankers burn in Hormuz"),
]

BRIEFS_L = [
    "13. US Army to detonate tonnes of unstable explosives in Iowa",
    "14. Houthi ballistic missile at western Saudi Arabia intercepted",
    "15. Albanese: COP31 failure shows 'hard geopolitical times'",
    "16. UK–EU Brexit reset deal: Burnham calls it 'landmark'",
    "17. Thousands march in Lisbon over the cost of living",
    "18. Russia-bound ship towed after attack in Gulf of Finland",
    "19. Nepal's PM Shah holds bilateral talks with PM Modi in Delhi",
    "20. Guru Nanak Jayanti marked — 'Sewa, Simran aur Sangat'",
    "21. Uttar Pradesh runs air-raid and blackout drills in 75 districts",
    "22. Indonesia factory fire UPDATE: 7 bodies found, 50 still missing",
    "23. India chase a famous win on day five; New Zealand 119/2",
    "24. India win the ODI series in New Zealand 3–2; Phillips player of series",
    "25. Anupama retains the IBSF women's world snooker title",
    "26. Rajya Sabha MP Ramrao Wadkute dies of a heart attack in Delhi",
    "27. Kota pilgrim bus tragedy in Rajasthan: nine killed",
    "28. Tata Steel sells tube business to APL Apollo for ₹28,000 crore",
]

BRIEFS_R = [
    "29. SpiceJet pilots seek urgent audit; IndiGo holds 65.9% of home market",
    "30. IFFI 2026 hosts a BRICS roundtable in Goa",
    "31. Modi opens AI centre at IIT Patna; ₹400 crore of research projects",
    "32. Chief Justice Surya Kant: AI guidelines a must in legal education",
    "33. JEE Main 2027 Session 1 registration closes today",
    "34. Google invests $5 million in AI research at IIT Kharagpur",
    "35. India–EU free trade pact likely to be signed 16 Dec in Brussels",
    "36. Trump criticises Schumer amid Democratic leadership push",
    "37. FBI probes suspected hack of its criminal justice database",
    "38. Miley Cyrus marries Maxx Morando in California",
    "39. Alcaraz beats Zverev for his first ATP Finals title",
    "40. Swimmer crosses the Strait of Hormuz for Iran's wildlife",
    "41. US declassifies more UFO footage filmed over the Middle East",
    "42. World Chess Championship captivates fans worldwide",
    "43. Mets agree $95 million, eight-year deal with A.J. Ewing",
]

dc = ("Xi–Trump–Putin trilateral summit — 19 NOV 2026 · "
      "Russian missiles & drones fell in Poland — incident 20 NOV · "
      "Paolo Bulgari died — reported 22 NOV 2026 · "
      "Ukrainian strike on the Kerch Bridge — reported 22 NOV · "
      "South Korea's education minister quit — first reported 22 NOV · "
      "Indonesia candy-factory fire AS AN EVENT — 22 NOV 2026")
DATE_CHECK = dc.split(" · ")

REGION_STRIP = [("MIDDLE EAST", 4), ("EUROPE", 9), ("NORTH AMERICA", 7),
                ("SOUTH ASIA", 16), ("ASIA-PACIFIC", 3), ("AFRICA", 1), ("GLOBAL", 3)]

MAP_ROWS = [
    "          oooo                                                     ",
    "   oooooooooooo      oo  oooooooo oooooooooo                       ",
    "  oooooooooooooo    oooooooooooooooooooooooooooo  oo               ",
    "   ooooooooooo      oooooooooooooooooooooooooooooooo               ",
    "    ooooooo          ooooo oooooooooooooooooooooo  oooo            ",
    "     oooo             oo    ooooooooooooooooooo      oo            ",
    "      oo                    ooooooooooooooooo                      ",
    "      ooo                    ooooooo         o                   ",
    "       ooo                    ooooo           o                   ",
    "       oooo                    ooo                                ",
    "        oooo                    oo              o                 ",
    "        ooooo                    oo              o                 ",
    "         oooo                                  ooo                 ",
    "         ooooo                                ooooo                ",
    "          oooo                                 ooo                 ",
    "          ooo                                                ",
    "          oo                                                 ",
]
PINS = {1: (40, 6), 2: (41, 7), 3: (35, 3), 4: (34, 5), 5: (34, 2), 6: (8, 5),
        7: (10, 4), 8: (62, 13), 9: (31, 3), 10: (36, 4), 11: (33, 7), 12: (47, 2)}


# ---------------------------------------------------------------- drawing
def header(d):
    d.rectangle([0, 0, W, 24], fill=INK)
    d.text((14, 5), "THE FIRST LIGHT POST", font=fb(13), fill=(245, 240, 230))
    kick = "43 STORIES · 7 REGIONS · EVERY ONE FROM 23 NOVEMBER 2026"
    d.text((W - 14 - tw(d, kick, fb(13)), 5), kick, font=fb(13), fill=(245, 200, 150))
    date = "Monday 23 November 2026"
    f = F("PlayfairDisplay-Black.ttf", 72)
    d.text(((W - tw(d, date, f)) / 2, 24), date, font=f, fill=INK)
    name = "THE FIRST LIGHT POST"
    d.text(((W - tw(d, name, fb(30))) / 2, 112), name, font=fb(30), fill=ACCENT)
    sub = "Tankers burn in the Strait of Hormuz  ·  Kyiv boy pulled alive from the rubble  ·  Democrats take the House 258–173"
    d.text(((W - tw(d, sub, fr(14))) / 2, 146), sub, font=fr(14), fill=MUTE)
    d.line([14, 164, W - 14, 164], fill=RULE, width=2)
    x, y = 14, 170
    for region, n in REGION_STRIP:
        d.rectangle([x, y + 2, x + 10, y + 14], fill=REGION_COLORS[region])
        label = "%s %d" % (region, n)
        d.text((x + 15, y), label, font=fb(13), fill=INK)
        x += 15 + tw(d, label, fb(13)) + 18
    d.line([14, 192, W - 14, 192], fill=RULE, width=1)
    x, y = 14, 198
    d.text((x, y), "THE DAY IN UTC", font=fb(11), fill=ACCENT)
    x += tw(d, "THE DAY IN UTC", fb(11)) + 14
    for t, ev in TL:
        d.text((x, y), t + " ", font=fb(11), fill=INK)
        x += tw(d, t + " ", fb(11))
        d.text((x, y), ev, font=fr(11), fill=MUTE)
        x += tw(d, ev, fr(11)) + 15
    d.line([14, 218, W - 14, 218], fill=RULE, width=2)


def chip(d, x, y, text):
    f = fb(11)
    w = tw(d, text, f) + 12
    d.rectangle([x, y, x + w, y + 16], fill=STATUS_COLORS[text])
    d.text((x + 6, y + 2), text, font=f, fill=(255, 255, 255))
    return w


def card_head(d, x, y, w, num, loc, region, cat, status, src, badge=22):
    d.rectangle([x, y, x + w, y + 4], fill=REGION_COLORS[region])
    d.rectangle([x + 8, y + 9, x + 8 + badge, y + 9 + badge], fill=INK)
    ns = str(num)
    d.text((x + 8 + badge / 2 - tw(d, ns, fb(14)) / 2, y + 13), ns, font=fb(14), fill=(255, 255, 255))
    d.text((x + 16 + badge, y + 10), loc, font=fb(12), fill=INK)
    chip(d, x + w - 8 - (tw(d, status, fb(11)) + 12), y + 9, status)
    meta = "%s · %s — Source: %s" % (region, cat, src)
    d.text((x + 16 + badge, y + 25), meta, font=fr(10), fill=MUTE)


def lead(d, x, y, w, h, region, topic, src, head, deck, kind, num=1, loc="", status="REPORTED"):
    """The big lead card."""
    d.rectangle([x, y, x + w, y + h], fill=PANEL, outline=RULE, width=1)
    card_head(d, x, y, w, num, loc, region, topic, status, src, badge=26)
    icon(d, kind, x + w - 76, y + 46, 60, ACCENT)
    ty = y + 44
    for ln in wrap(d, head, fb(31), w - 104)[:2]:
        d.text((x + 10, ty), ln, font=fb(31), fill=INK)
        ty += 36
    for ln in wrap(d, deck, fr(15), w - 20)[:2]:
        d.text((x + 10, ty + 4), ln, font=fr(15), fill=(50, 48, 44))
        ty += 19


def mini(d, x, y, w, h, region, topic, src, head, deck, kind, num=0, loc="", status="REPORTED"):
    """A side lead card: compact header, one-line headline, one deck line."""
    d.rectangle([x, y, x + w, y + h], fill=PANEL, outline=RULE, width=1)
    card_head(d, x, y, w, num, loc, region, topic, status, src)
    d.text((x + 10, y + 36), head, font=fb(28), fill=INK)
    fl = wrap(d, deck, fr(15), w - 20, max_lines=1)
    d.text((x + 10, y + 65), fl[0], font=fr(15), fill=(50, 48, 44))


def tall_card(d, x, y, w, h, t):
    num, region, topic, src, head, deck, kind = t
    loc, cat, status = topic.split("|")
    d.rectangle([x, y, x + w, y + h], fill=PANEL, outline=RULE, width=1)
    card_head(d, x, y, w, num, loc, region, cat, status, src)
    ty = y + 42
    for ln in wrap(d, head, fb(28), w - 20)[:2]:
        d.text((x + 10, ty), ln, font=fb(28), fill=INK)
        ty += 31
    icon(d, kind, x + w - 44, y + h - 44, 32, REGION_COLORS[region])
    for ln in wrap(d, deck, fr(15), w - 56)[:2]:
        d.text((x + 10, ty + 2), ln, font=fr(15), fill=(50, 48, 44))
        ty += 18


def grid_card(d, x, y, w, h, t):
    num, region, topic, src, head, deck, kind = t
    loc, cat, status = topic.split("|")
    d.rectangle([x, y, x + w, y + h], fill=PANEL, outline=RULE, width=1)
    card_head(d, x, y, w, num, loc, region, cat, status, src)
    ty = y + 38
    tlines = wrap(d, head, fb(28), w - 20)[:2]
    for ln in tlines:
        d.text((x + 10, ty), ln, font=fb(28), fill=INK)
        ty += 27
    icon(d, kind, x + w - 38, y + h - 38, 28, REGION_COLORS[region])
    maxf = 2 if len(tlines) == 1 else 1
    for ln in wrap(d, deck, fr(15), w - 52)[:maxf]:
        d.text((x + 10, ty + 1), ln, font=fr(15), fill=(50, 48, 44))
        ty += 17


def numbers_box(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 22, 20))
    d.text((x + 10, y + 7), "THE DAY IN NUMBERS", font=fb(14), fill=(245, 200, 150))
    colw = (w - 20) // 3
    for i, (big, label) in enumerate(NUMS):
        cx = x + 10 + (i % 3) * colw
        cy = y + 30 + (i // 3) * 38
        d.text((cx, cy), big, font=fb(23), fill=(255, 255, 255))
        d.text((cx, cy + 27), label, font=fr(9), fill=(200, 195, 185))


def dotted_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=PANEL, outline=RULE, width=1)
    d.text((x + 10, y + 6), "WHERE IT HAPPENED — dot map, pins = card numbers", font=fb(11), fill=INK)
    cols = 68
    rows = len(MAP_ROWS)
    cw = (w - 20) / cols
    chh = (h - 48) / rows
    r = max(1.3, min(cw, chh) * 0.32)
    for ry, row in enumerate(MAP_ROWS):
        for rx, ch in enumerate(row):
            if ch == "o":
                cx = x + 10 + rx * cw + cw / 2
                cy = y + 26 + ry * chh + chh / 2
                d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(150, 145, 135))
    for num, (rx, ry) in PINS.items():
        cx = x + 10 + rx * cw + cw / 2
        cy = y + 26 + ry * chh + chh / 2
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=ACCENT)
        ns = str(num)
        d.text((cx - tw(d, ns, fb(10)) / 2, cy - 6), ns, font=fb(10), fill=(255, 255, 255))
    ly = y + h - 15
    lx = x + 10
    for abbr, region in [("ME", "MIDDLE EAST"), ("EU", "EUROPE"), ("NA", "NORTH AMERICA"),
                         ("SA", "SOUTH ASIA"), ("AP", "ASIA-PACIFIC"), ("AF", "AFRICA"), ("GL", "GLOBAL")]:
        d.rectangle([lx, ly + 1, lx + 8, ly + 9], fill=REGION_COLORS[region])
        d.text((lx + 11, ly), abbr, font=fr(9), fill=MUTE)
        lx += 11 + tw(d, abbr, fr(9)) + 10


def date_check_box(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(250, 240, 235), outline=(170, 40, 30), width=2)
    d.text((x + 10, y + 6), "DATE CHECK — NOT TODAY'S NEWS", font=fb(12), fill=(170, 40, 30))
    cy = y + 24
    for item in DATE_CHECK:
        for ln in wrap(d, "✕ " + item, fr(11), w - 20):
            if cy > y + h - 13:
                break
            d.text((x + 10, cy), ln, font=fr(11), fill=(90, 30, 25))
            cy += 12


def also_block(d, x, y, w):
    d.text((x, y), "ALSO ON MONDAY — STORIES 13 TO 43", font=fb(14), fill=ACCENT)
    briefs = BRIEFS_L + BRIEFS_R
    colw = w // 4
    cy = y + 20
    per_col = 8
    for i, line in enumerate(briefs):
        cx = x + (i // per_col) * colw
        yy = cy + (i % per_col) * 14
        ll = wrap(d, line, fsr(13), colw - 8, max_lines=1)
        d.text((cx, yy), ll[0], font=fsr(13), fill=INK)


def footer(d):
    y = 998
    d.line([14, y - 4, W - 14, y - 4], fill=RULE, width=1)
    l1 = "HOW SURE: REPORTED = confirmed by a named source · CLAIM = one side's account, labelled as such · ONGOING = still developing · OFFICIAL = on the record of a body or court."
    d.text((14, y), l1, font=fr(11), fill=MUTE)
    l2 = "Every story happened, or was first reported, on Monday 23 November 2026. Contested claims are attributed.  ·  Original drawings."
    d.text((14, y + 14), l2, font=fr(11), fill=MUTE)


def build(variant):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    header(d)
    lead_w = 492 if variant == "A" else 325
    lead(d, 14, 226, lead_w, 168, "MIDDLE EAST", "WAR", "AP live wire",
         "Tankers burn in the Strait of Hormuz",
         "Tankers were set ablaze as the Iran–US war widened into the Gulf; the IRGC warned of unrest.",
         "flame", num=1, loc="STRAIT OF HORMUZ", status="REPORTED")
    if variant == "A":
        mini(d, 518, 226, 492, 81, "MIDDLE EAST", "WAR", "AP / AFP wire",
             "IRGC claims Patriot radars hit",
             "Two radars destroyed at a US base, Tehran says; unconfirmed.",
             "radar", num=2, loc="BAHRAIN", status="CLAIM")
        mini(d, 518, 313, 492, 81, "EUROPE", "WAR", "BBC News",
             "Kyiv boy, 7, pulled out alive",
             "Freed from the rubble in Kyiv after a Russian strike; six killed.",
             "rubble", num=3, loc="KYIV, UKRAINE", status="REPORTED")
    else:
        # variant B: the three leads as one equal row, lead card narrower
        tall_card(d, 14 + 1 * (325 + 6), 226, 325, 168,
                  (2, "MIDDLE EAST", "BAHRAIN|WAR|CLAIM", "AP / AFP wire",
                   "IRGC claims Patriot radars hit",
                   "Two radars destroyed at a US base, Tehran says; unconfirmed.", "radar"))
        tall_card(d, 14 + 2 * (325 + 6), 226, 325, 168,
                  (3, "EUROPE", "KYIV, UKRAINE|WAR|REPORTED", "BBC News",
                   "Kyiv boy, 7, pulled out alive",
                   "Freed from the rubble in Kyiv after a Russian strike; six killed.", "rubble"))
    gy, by, also_y = 400, 742, 858
    gx, gw, gh, gap = 14, 325, 108, 6
    for i, t in enumerate(grid):
        cx = gx + (i % 3) * (gw + gap)
        cy = gy + (i // 3) * (gh + gap)
        grid_card(d, cx, cy, gw, gh, t)
    numbers_box(d, 14, by, 340, 108)
    dotted_map(d, 362, by, 270, 108)
    date_check_box(d, 640, by, 370, 108)
    also_block(d, 14, also_y, 996)
    footer(d)
    return img


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "A"
    out = sys.argv[2] if len(sys.argv) > 2 else "/tmp/ni23g4-akun4-%s.png" % which
    img = build(which)
    if "--entry" in sys.argv:
        # final entry: palette-quantised to keep the file lean (flat artwork)
        img = img.quantize(colors=256, method=Image.MEDIANCUT)
    img.save(out, optimize=True)
    print("saved", out)
