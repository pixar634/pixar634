"""Builds the animated SVGs for the pixar634 GitHub profile README.

GitHub shows README SVGs through <img>: CSS @keyframes run, scripts and
external fonts do not. So every SVG embeds Nohemi (unmodified woff2, see
fonts/NOHEMI-LICENSE.txt) and animates with CSS only.

Every element's resting style is its final state and keyframes animate *from*
hidden, so with prefers-reduced-motion (animation:none) everything still shows.

Text widths come from Chrome measuring the real font (measure.json), not guesses.
Needs fonts/Nohemi-{Regular,Medium,SemiBold}.woff2 (not committed; copy them from the
Lighthouse repo's lighthouse-frontend/public/fonts).
Run: python gen.py  -> assets/profile/{hero,tile-*}-{light,dark}.svg
"""
import base64
import json
import math
import os
import subprocess
import tempfile
from html import escape

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "assets", "profile")
os.makedirs(OUT, exist_ok=True)
CACHE = os.path.join(ROOT, "measure.json")
CHROME = next(p for p in [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/usr/bin/google-chrome", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
] if os.path.exists(p))

FONTS = {w: base64.b64encode(open(os.path.join(ROOT, "fonts", f"Nohemi-{n}.woff2"), "rb").read()).decode()
         for w, n in [(400, "Regular"), (500, "Medium"), (600, "SemiBold")]}
FACE = "".join(f"@font-face{{font-family:N;font-weight:{w};src:url(data:font/woff2;base64,{b64}) format('woff2')}}"
               for w, b64 in FONTS.items())

THEMES = {
    "light": dict(bg="#F4F1EA", card="#F8F5EF", line="#1C1915", line_o=".10", ink="#1C1915", ink2="#3F3A36",
                  ink3="#6B645C", accent="#A83F1C", amber="#A2661F", mint="#5DCAA5", chip="#EEE9DF",
                  glow_a=".30", glow_b=".16", beam="#A2661F", beam_o=".10", grid_o=".22", noise_o=".05",
                  bubble_me="#A83F1C", bubble_me_o=".14"),
    "dark": dict(bg="#0F0F12", card="#16161B", line="#FFFFFF", line_o=".08", ink="#EDEAE4", ink2="#BDB8B0",
                 ink3="#8A857D", accent="#5DCAA5", amber="#E0A458", mint="#5DCAA5", chip="#1F1F26",
                 glow_a=".20", glow_b=".13", beam="#5DCAA5", beam_o=".12", grid_o=".14", noise_o=".07",
                 bubble_me="#5DCAA5", bubble_me_o=".16"),
}
EASE = "cubic-bezier(.2,.7,.2,1)"
INSET = 7  # transparent margin inside each SVG; two tiles side by side get a 14px gutter

# ---- text measurement -------------------------------------------------------
_cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
_missing = set()


def W(text, size, weight=400, ls=0.0):
    key = f"{weight}|{size}|{ls}|{text}"
    if key in _cache:
        return _cache[key]
    _missing.add(key)
    return len(text) * size * 0.56


def measure():
    keys = sorted(_missing)
    page = ("<!doctype html><html><body><svg width='2000' height='200'><style>" + FACE +
            "</style><text id='t' x='0' y='100' font-family='N'></text></svg><pre id='o'></pre><script>"
            "const K=" + json.dumps(keys) + ";"
            "Promise.all([400,500,600].map(w=>document.fonts.load(w+' 20px N'))).then(()=>{"
            "const t=document.getElementById('t'),r={};"
            "for(const k of K){const [w,s,ls,...x]=k.split('|');t.setAttribute('font-weight',w);"
            "t.setAttribute('font-size',s);t.setAttribute('letter-spacing',ls);t.textContent=x.join('|');"
            "r[k]=Math.round(t.getComputedTextLength()*10)/10;}"
            "document.getElementById('o').textContent='@@'+JSON.stringify(r)+'@@';});</script></body></html>")
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(page)
    dom = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--virtual-time-budget=5000",
                          "--dump-dom", "file:///" + f.name.replace("\\", "/")],
                         capture_output=True, text=True, encoding="utf-8").stdout
    os.unlink(f.name)
    _cache.update(json.loads(dom.split("@@")[1]))
    json.dump(_cache, open(CACHE, "w"), indent=0, sort_keys=True)
    _missing.clear()


# ---- shared pieces ----------------------------------------------------------
def e(s):
    return escape(s, quote=True)


def svg_doc(w, h, label, title, css, body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{e(label)}"><title>{e(title)}</title><defs>{defs}</defs>'
            f'<style>{FACE}text{{font-family:N,ui-sans-serif,system-ui,sans-serif}}{css}'
            f'@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>{body}</svg>')


def card(p, w, h, T, r=22):
    """Card ground, hairline border and a faint top sheen. Returns (defs, under, over, clip-id)."""
    x, y, cw, ch = INSET, INSET, w - 2 * INSET, h - 2 * INSET
    defs = (f'<clipPath id="{p}c"><rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="{r}"/></clipPath>'
            f'<linearGradient id="{p}sh" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".05"/>'
            f'<stop offset=".4" stop-color="#fff" stop-opacity="0"/></linearGradient>')
    under = f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="{r}" fill="{T["card"]}"/>'
    over = (f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="{r}" fill="url(#{p}sh)"/>'
            f'<rect x="{x + .5}" y="{y + .5}" width="{cw - 1}" height="{ch - 1}" rx="{r - .5}" fill="none" '
            f'stroke="{T["line"]}" stroke-opacity="{T["line_o"]}"/>')
    return defs, under, over, f"{p}c"


def drift_glow(p, cx, cy, r, color, op, dx, dy, dur, k):
    """A soft radial light that drifts back and forth. Gradient fill, no blur filter: cheap to paint."""
    defs = (f'<radialGradient id="{p}g{k}"><stop offset="0" stop-color="{color}" stop-opacity="{op}"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>')
    css = (f'@keyframes {p}d{k}{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate({dx}px,{dy}px)}}}}'
           f'.{p}d{k}{{animation:{p}d{k} {dur}s ease-in-out infinite}}')
    body = f'<circle class="{p}d{k}" cx="{cx}" cy="{cy}" r="{r}" fill="url(#{p}g{k})"/>'
    return defs, css, body


def kicker(p, x, y, text, T, live=False):
    """Small uppercase label; a live one carries a pulsing mint dot."""
    out, css, tx = "", "", x
    if live:
        css = (f'@keyframes {p}lv{{0%{{r:4;opacity:.55}}100%{{r:11;opacity:0}}}}'
               f'.{p}lv{{animation:{p}lv 2.2s ease-out infinite}}')
        out = (f'<circle class="{p}lv" cx="{x + 4}" cy="{y - 4}" r="4" fill="{T["mint"]}" opacity="0"/>'
               f'<circle cx="{x + 4}" cy="{y - 4}" r="4" fill="{T["mint"]}"/>')
        tx = x + 16
    out += (f'<text x="{tx}" y="{y}" fill="{T["ink3"]}" font-size="12" font-weight="500" '
            f'letter-spacing="1.6">{e(text.upper())}</text>')
    return css, out


# ---- hero -------------------------------------------------------------------
HERO_W, HERO_H = 846, 392
ROLES = ["the API.", "the web app.", "the native app.", "the whole product."]
STACK = ["TypeScript", "React", "React Native", "FastAPI", "PostgreSQL", "Python"]


def hero(T):
    p = "h"
    w, h = HERO_W, HERO_H
    cdefs, under, over, clip = card(p, w, h, T, r=26)
    defs, css, layers = [cdefs], [], []

    # Light: two drifting glows, a dot grid that fades out, and a whisper of grain.
    for k, (cx, cy, r, col, op, dx, dy, dur) in enumerate([
        (700, 120, 330, T["mint"], T["glow_a"], -60, 40, 18),
        (260, 420, 360, T["amber"], T["glow_b"], 80, -30, 23),
        (840, 400, 240, T["accent"], T["glow_b"], -40, -50, 27),
    ]):
        d, c, b = drift_glow(p, cx, cy, r, col, op, dx, dy, dur, k)
        defs.append(d), css.append(c), layers.append(b)
    defs.append(
        f'<pattern id="{p}dot" width="22" height="22" patternUnits="userSpaceOnUse">'
        f'<circle cx="11" cy="11" r="1" fill="{T["ink"]}"/></pattern>'
        f'<radialGradient id="{p}fade" cx=".78" cy=".42" r=".62"><stop offset="0" stop-color="#fff"/>'
        f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
        f'<mask id="{p}m"><rect width="{w}" height="{h}" fill="url(#{p}fade)"/></mask>'
        f'<filter id="{p}n" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" '
        f'baseFrequency=".85" numOctaves="2" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/></filter>')
    layers.append(f'<rect width="{w}" height="{h}" fill="url(#{p}dot)" opacity="{T["grid_o"]}" mask="url(#{p}m)"/>')

    # The beacon: a mint core with pulse rings and a two-sided beam turning slowly behind it.
    bx, by, L, half = 708, 176, 900, 5.5
    defs.append(f'<linearGradient id="{p}bm" gradientUnits="userSpaceOnUse" x1="{bx}" y1="{by}" x2="{bx + L}" y2="{by}">'
                f'<stop offset="0" stop-color="{T["beam"]}" stop-opacity="{T["beam_o"]}"/>'
                f'<stop offset=".5" stop-color="{T["beam"]}" stop-opacity="0"/></linearGradient>')

    def wedge_pts(deg):
        a = math.radians(deg)
        return (f'{bx},{by} {bx + L * math.cos(a):.1f},{by + L * math.sin(a):.1f} '
                f'{bx + L * math.cos(a):.1f},{by - L * math.sin(a):.1f}')
    css.append(f'@keyframes {p}sp{{to{{transform:rotate(360deg)}}}}'
               f'.{p}sp{{transform-box:view-box;transform-origin:{bx}px {by}px;animation:{p}sp 16s linear infinite}}')
    beam = (f'<polygon points="{wedge_pts(half * 1.9)}" fill="url(#{p}bm)" opacity=".45"/>'
            f'<polygon points="{wedge_pts(half * .9)}" fill="url(#{p}bm)"/>')
    # Rests on a diagonal, so with motion off the beam never sits flat across the text.
    layers.append(f'<g class="{p}sp"><g transform="rotate(-34 {bx} {by})">{beam}'
                  f'<g transform="rotate(180 {bx} {by})">{beam}</g></g></g>')
    css.append(f'@keyframes {p}rg{{0%{{r:9;opacity:.6}}100%{{r:64;opacity:0}}}}'
               f'.{p}rg{{animation:{p}rg 3.2s ease-out infinite}}.{p}rg2{{animation-delay:1.6s}}')
    layers.append(
        f'<circle cx="{bx}" cy="{by}" r="30" fill="{T["mint"]}" opacity=".16"/>'
        f'<circle class="{p}rg" cx="{bx}" cy="{by}" r="9" fill="none" stroke="{T["mint"]}" stroke-width="1.5" opacity="0"/>'
        f'<circle class="{p}rg {p}rg2" cx="{bx}" cy="{by}" r="9" fill="none" stroke="{T["mint"]}" stroke-width="1.5" opacity="0"/>'
        f'<circle cx="{bx}" cy="{by}" r="8" fill="{T["mint"]}" stroke="{T["card"]}" stroke-width="3"/>')
    layers.append(f'<rect width="{w}" height="{h}" filter="url(#{p}n)" opacity="{T["noise_o"]}"/>')

    # Entrance: everything rises once and stays. Resting state is the final state.
    css.append(f'@keyframes {p}up{{from{{opacity:0;transform:translateY(14px)}}}}'
               f'.{p}u{{animation:{p}up .9s {EASE} both}}')

    def up(delay):
        return f'class="{p}u" style="animation-delay:{delay:.2f}s"'

    x0 = 44
    txt = []
    # Status pill.
    pill = "Open to full-stack roles"
    pw = W(pill, 14, 500) + 42
    css.append(f'@keyframes {p}pl{{0%{{r:4;opacity:.6}}100%{{r:12;opacity:0}}}}.{p}pl{{animation:{p}pl 2s ease-out infinite}}')
    txt.append(f'<g {up(.05)}><rect x="{x0}" y="40" width="{pw:.1f}" height="32" rx="16" fill="{T["chip"]}" '
               f'stroke="{T["line"]}" stroke-opacity="{T["line_o"]}"/>'
               f'<circle class="{p}pl" cx="{x0 + 18}" cy="56" r="4" fill="{T["mint"]}" opacity="0"/>'
               f'<circle cx="{x0 + 18}" cy="56" r="4" fill="{T["mint"]}"/>'
               f'<text x="{x0 + 31}" y="61" fill="{T["ink2"]}" font-size="14" font-weight="500">{e(pill)}</text></g>')
    # Name.
    txt.append(f'<text {up(.15)} x="{x0 - 3}" y="152" fill="{T["ink"]}" font-size="76" font-weight="600" '
               f'letter-spacing="-2.6">Soumava Paul</text>')
    # Role + experience.
    role, yrs = "Full-stack developer", "8+ years"
    rw = W(role, 28, 400, -0.4)
    txt.append(f'<g {up(.3)}><text x="{x0}" y="204" fill="{T["ink2"]}" font-size="28" letter-spacing="-.4">{role}</text>'
               f'<text x="{x0 + rw + 12:.1f}" y="204" fill="{T["ink3"]}" font-size="28">·</text>'
               f'<text x="{x0 + rw + 32:.1f}" y="204" fill="{T["amber"]}" font-size="28" font-weight="600" '
               f'letter-spacing="-.4">{yrs}</text></g>')
    # "I build ..." with a rotating object. Each word shares one keyframe set, phased by delay.
    lead = "I build"
    lw = W(lead, 28, 400, -0.4)
    D, n, ein = 2.6, len(ROLES), 0.42
    P = D * n
    a1, a2, a3 = ein / P * 100, (D - ein) / P * 100, D / P * 100
    css.append(f'@keyframes {p}rw{{0%{{opacity:0;transform:translateY(20px)}}{a1:.2f}%,{a2:.2f}%{{opacity:1;transform:none}}'
               f'{a3:.2f}%,100%{{opacity:0;transform:translateY(-20px)}}}}'
               f'.{p}rw{{animation:{p}rw {P:.1f}s {EASE} infinite backwards}}')
    rx = x0 + lw + 10
    defs.append(f'<clipPath id="{p}rc"><rect x="{rx - 4:.1f}" y="216" width="520" height="42"/></clipPath>')
    hidden = ' opacity="0"'  # only the first word shows when motion is off
    words = "".join(
        f'<text class="{p}rw" style="animation-delay:{.9 + k * D:.2f}s" x="{rx:.1f}" y="246" fill="{T["accent"]}" '
        f'font-size="28" font-weight="600" letter-spacing="-.4"{hidden if k else ""}>{e(r)}</text>'
        for k, r in enumerate(ROLES))
    txt.append(f'<g {up(.42)}><text x="{x0}" y="246" fill="{T["ink2"]}" font-size="28" letter-spacing="-.4">{lead}</text>'
               f'<g clip-path="url(#{p}rc)">{words}</g></g>')
    # Stack chips.
    cx = x0
    for k, s in enumerate(STACK):
        cw = W(s, 14, 500) + 28
        txt.append(f'<g {up(.6 + k * .06)}><rect x="{cx:.1f}" y="300" width="{cw:.1f}" height="34" rx="17" '
                   f'fill="{T["card"]}" fill-opacity=".7" stroke="{T["line"]}" stroke-opacity="{T["line_o"]}"/>'
                   f'<text x="{cx + 14:.1f}" y="322" fill="{T["ink2"]}" font-size="14" font-weight="500">{e(s)}</text></g>')
        cx += cw + 8

    body = (f'{under}<g clip-path="url(#{clip})">{"".join(layers)}</g>{over}{"".join(txt)}')
    label = ("Soumava Paul. Open to full-stack roles. Full-stack developer, 8+ years. I build the API, the web app, "
             "the native app, the whole product. Stack: " + ", ".join(STACK) + ".")
    return svg_doc(w, h, label, "Soumava Paul", "".join(css), body, "".join(defs))


# ---- tiles ------------------------------------------------------------------
def tile_frame(p, w, h, T, glow_xy, glow_col):
    cdefs, under, over, clip = card(p, w, h, T)
    d, c, b = drift_glow(p, glow_xy[0], glow_xy[1], 220, glow_col, T["glow_b"], -30, 20, 14, 0)
    return [cdefs, d], [c], under, f'<g clip-path="url(#{clip})">{b}', over


def text_block(x, y, title, lines, T, size=34):
    out = f'<text x="{x - 1}" y="{y}" fill="{T["ink"]}" font-size="{size}" font-weight="600" letter-spacing="-1">{e(title)}</text>'
    for k, l in enumerate(lines):
        out += f'<text x="{x}" y="{y + 30 + k * 22}" fill="{T["ink3"]}" font-size="15.5">{e(l)}</text>'
    return out


def contour(cx, cy, r, sx=1.3, seed=0.0):
    pts = []
    for i in range(72):
        t = i / 72 * 2 * math.pi
        rr = r * (1 + .13 * math.sin(3 * t + seed + r * .04) + .07 * math.sin(5 * t + 1.3 + seed))
        pts.append((cx + rr * math.cos(t) * sx, cy + rr * math.sin(t)))
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z"


def tile_lighthouse(T):
    p, w, h = "tl", 520, 248
    defs, css, under, inner, over = tile_frame(p, w, h, T, (440, 60), T["mint"])
    # Topography + a route that draws itself between three stops, then rests and resets.
    cx, cy = 400, 128
    topo = "".join(f'<path d="{contour(cx, cy, r, seed=.6)}" fill="none" stroke="{T["ink"]}" '
                   f'stroke-opacity="{.07 + i * .025:.3f}" stroke-width="1"/>' for i, r in enumerate([92, 74, 57, 41, 26, 13]))
    stops = [(318, 196), (372, 118), (452, 86)]
    route = f'M{stops[0][0]},{stops[0][1]} C340,160 350,130 {stops[1][0]},{stops[1][1]} S420,70 {stops[2][0]},{stops[2][1]}'
    P = 7.0
    css.append(f'@keyframes {p}rt{{0%{{stroke-dashoffset:1;opacity:1}}45%,85%{{stroke-dashoffset:0;opacity:1}}'
               f'95%,100%{{stroke-dashoffset:0;opacity:0}}}}'
               f'.{p}rt{{stroke-dasharray:1;animation:{p}rt {P}s {EASE} infinite}}')
    pins = ""
    for k, (x, y) in enumerate(stops):
        at = [0, 22, 45][k]
        css.append(f'@keyframes {p}p{k}{{0%,{at}%{{transform:scale(0)}}{at + 6}%{{transform:scale(1.25)}}'
                   f'{at + 10}%,85%{{transform:scale(1)}}95%,100%{{transform:scale(0)}}}}'
                   f'.{p}p{k}{{transform-box:fill-box;transform-origin:center;animation:{p}p{k} {P}s ease-out infinite}}')
        fill = T["mint"] if k == 2 else T["accent"]
        pins += (f'<g class="{p}p{k}"><circle cx="{x}" cy="{y}" r="11" fill="{fill}" opacity=".18"/>'
                 f'<circle cx="{x}" cy="{y}" r="5.5" fill="{fill}" stroke="{T["card"]}" stroke-width="2.5"/></g>')
    art = (f'{topo}<path class="{p}rt" d="{route}" pathLength="1" fill="none" stroke="{T["accent"]}" '
           f'stroke-width="2.2" stroke-linecap="round"/>{pins}')
    kc, kt = kicker(p, 30, 44, "Founder · Live", T, live=True)
    css.append(kc)
    link = "letsgolighthouse.co.in ↗"
    body = (f'{under}{inner}{art}</g>{over}{kt}'
            f'{text_block(30, 104, "Lighthouse", ["Weekend discovery for India.", "Web, API and native,", "one backend."], T)}'
            f'<text x="30" y="214" fill="{T["accent"]}" font-size="14" font-weight="500">{e(link)}</text>')
    return svg_doc(w, h, "Lighthouse, founder project, live. Weekend discovery for India: web, API and native on one "
                         "backend. letsgolighthouse.co.in", "Lighthouse", "".join(css), body, "".join(defs))


def tile_prepster(T):
    p, w, h = "tp", 326, 248
    defs, css, under, inner, over = tile_frame(p, w, h, T, (300, 230), T["amber"])
    P = 8.0

    def show(cls, start, k):
        a = start / P * 100
        return (f'@keyframes {cls}{{0%,{a:.1f}%{{opacity:0;transform:translateY(8px)}}{a + 5:.1f}%,88%{{opacity:1;transform:none}}'
                f'96%,100%{{opacity:0;transform:none}}}}.{cls}{{animation:{cls} {P}s {EASE} infinite}}')
    # Interviewer (left) asks, you answer (right), interviewer is typing. Bars, not invented words.
    css.append(show(f"{p}b0", .3, 0) + show(f"{p}b1", 1.7, 1) + show(f"{p}b2", 3.2, 2))
    css.append(f'@keyframes {p}ty{{0%,60%,100%{{transform:translateY(0);opacity:.45}}30%{{transform:translateY(-3px);opacity:1}}}}'
               f'.{p}ty{{animation:{p}ty 1.1s ease-in-out infinite}}')

    def bars(x, y, ws, col, op):
        return "".join(f'<rect x="{x}" y="{y + i * 11}" width="{bw}" height="5" rx="2.5" fill="{col}" opacity="{op}"/>'
                       for i, bw in enumerate(ws))
    b0 = (f'<g class="{p}b0"><rect x="160" y="66" width="132" height="44" rx="14" fill="{T["chip"]}"/>'
          f'{bars(174, 78, [96, 64], T["ink3"], ".55")}</g>')
    b1 = (f'<g class="{p}b1"><rect x="186" y="120" width="112" height="44" rx="14" fill="{T["bubble_me"]}" '
          f'fill-opacity="{T["bubble_me_o"]}"/>{bars(200, 132, [78, 52], T["accent"], ".7")}</g>')
    dots = "".join(f'<circle class="{p}ty" style="animation-delay:{i * .15:.2f}s" cx="{178 + i * 12}" cy="195" r="3.5" '
                   f'fill="{T["ink3"]}"/>' for i in range(3))
    b2 = f'<g class="{p}b2"><rect x="160" y="178" width="62" height="34" rx="14" fill="{T["chip"]}"/>{dots}</g>'
    kc, kt = kicker(p, 30, 44, "AI · Open source", T)
    body = (f'{under}{inner}{b0}{b1}{b2}</g>{over}{kt}'
            f'{text_block(30, 104, "prepster", ["AI mock", "interviews."], T, size=30)}')
    return svg_doc(w, h, "prepster: AI mock interview bot. Open source.", "prepster", "".join(css), body, "".join(defs))


def tile_jobmagnet(T):
    p, w, h = "tj", 423, 178
    defs, css, under, inner, over = tile_frame(p, w, h, T, (380, 30), T["accent"])
    # A CV page; a scan line passes and the lines it crosses light up, then settle back.
    dx, dy, dw, dh = 296, 30, 96, 118
    lines = [(dy + 22 + i * 13, lw) for i, lw in enumerate([46, 70, 62, 72, 54, 68, 40])]
    P = 6.0
    for i, (ly, lw) in enumerate(lines):
        a = (8 + i * 6.5)
        css.append(f'@keyframes {p}l{i}{{0%,{a:.1f}%{{fill:{T["ink3"]};opacity:.35}}{a + 4:.1f}%,80%{{fill:{T["accent"]};opacity:.9}}'
                   f'95%,100%{{fill:{T["ink3"]};opacity:.35}}}}.{p}l{i}{{animation:{p}l{i} {P}s ease-out infinite}}')
    css.append(f'@keyframes {p}sc{{0%{{transform:translateY(0);opacity:0}}6%{{opacity:1}}60%{{transform:translateY({dh - 14}px);opacity:1}}'
               f'68%,100%{{transform:translateY({dh - 14}px);opacity:0}}}}.{p}sc{{animation:{p}sc {P}s {EASE} infinite}}')
    defs.append(f'<linearGradient id="{p}sg" x1="0" x2="1"><stop offset="0" stop-color="{T["accent"]}" stop-opacity="0"/>'
                f'<stop offset=".5" stop-color="{T["accent"]}" stop-opacity=".9"/><stop offset="1" stop-color="{T["accent"]}" stop-opacity="0"/></linearGradient>')
    page = (f'<rect x="{dx}" y="{dy}" width="{dw}" height="{dh}" rx="10" fill="{T["card"]}" stroke="{T["line"]}" '
            f'stroke-opacity=".14"/><circle cx="{dx + 18}" cy="{dy + 16}" r="6" fill="{T["ink3"]}" opacity=".3"/>'
            + "".join(f'<rect class="{p}l{i}" x="{dx + 12}" y="{ly + 6}" width="{lw}" height="4" rx="2" fill="{T["ink3"]}" opacity=".35"/>'
                      for i, (ly, lw) in enumerate(lines))
            + f'<rect class="{p}sc" x="{dx - 6}" y="{dy + 8}" width="{dw + 12}" height="2" fill="url(#{p}sg)" opacity="0"/>')
    kc, kt = kicker(p, 30, 44, "Python · Open source", T)
    body = (f'{under}{inner}{page}</g>{over}{kt}'
            f'{text_block(30, 92, "jobmagnet", ["Turn your CV into a hard", "to ignore candidature."], T, size=30)}')
    return svg_doc(w, h, "jobmagnet: turn your CV into a hard to ignore candidature. Python, open source.",
                   "jobmagnet", "".join(css), body, "".join(defs))


def tile_private(T):
    p, w, h = "tv", 423, 178
    defs, css, under, inner, over = tile_frame(p, w, h, T, (60, 190), T["mint"])
    kc, kt = kicker(p, 30, 44, "In private", T)
    chips, x = "", 30
    css.append(f'@keyframes {p}sh{{0%,100%{{opacity:.0}}50%{{opacity:.9}}}}')
    for k, name in enumerate(["jobtracker", "yodatrader", "autoops"]):
        cw = W(name, 14, 500) + 46
        lock = (f'<rect x="{x + 13}" y="{126}" width="11" height="9" rx="2" fill="{T["ink3"]}"/>'
                f'<path d="M{x + 15.5},{126} v-3 a3,3 0 0 1 6,0 v3" fill="none" stroke="{T["ink3"]}" stroke-width="1.6"/>')
        chips += (f'<rect x="{x:.1f}" y="110" width="{cw:.1f}" height="36" rx="18" fill="{T["chip"]}" '
                  f'stroke="{T["line"]}" stroke-opacity="{T["line_o"]}"/>{lock}'
                  f'<rect x="{x:.1f}" y="110" width="{cw:.1f}" height="36" rx="18" fill="none" stroke="{T["mint"]}" '
                  f'stroke-width="1.2" opacity="0" style="animation:{p}sh 6s ease-in-out {k * 2}s infinite"/>'
                  f'<text x="{x + 32:.1f}" y="133" fill="{T["ink2"]}" font-size="14" font-weight="500">{name}</text>')
        x += cw + 8
    body = (f'{under}{inner}</g>{over}{kt}'
            f'<text x="29" y="90" fill="{T["ink"]}" font-size="30" font-weight="600" letter-spacing="-1">Also building</text>{chips}')
    return svg_doc(w, h, "Also building, in private: jobtracker, yodatrader, autoops.", "Also building",
                   "".join(css), body, "".join(defs))


BUILDERS = {"hero": hero, "tile-lighthouse": tile_lighthouse, "tile-prepster": tile_prepster,
            "tile-jobmagnet": tile_jobmagnet, "tile-private": tile_private}


def build():
    return {(name, th): fn(T) for name, fn in BUILDERS.items() for th, T in THEMES.items()}


if __name__ == "__main__":
    out = build()
    if _missing:
        measure()
        out = build()
    for (name, th), svg in out.items():
        with open(os.path.join(OUT, f"{name}-{th}.svg"), "w", encoding="utf-8") as f:
            f.write(svg)
    print("\n".join(f"{n}-{t}.svg  {len(s) // 1024} KB" for (n, t), s in out.items()))
