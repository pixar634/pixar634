"""Builds the animated SVGs for the pixar634 GitHub profile README.

GitHub renders README SVGs through <img>, so CSS @keyframes animate but
scripts and external fonts do not load. Everything here is pure CSS.
Run: python gen.py  -> writes assets/profile/*.svg
"""
import html
import os
import random

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "profile")
os.makedirs(OUT, exist_ok=True)

FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
BG, PANEL, INK, DIM, MINT, AMBER, LINE = (
    "#0F0F12", "#1A1A1F", "#E8E6E1", "#8A8780", "#5DCAA5", "#E0A458", "#2A2A31")
CW = 7.85     # px per monospace char at 13px; reveal-mask width estimate
LOOP = 18.0   # seconds for one full typing cycle


def esc(s):
    return html.escape(s, quote=True)


def hero():
    W, H = 846, 378
    # (text, colour, start s, typing s)
    lines = [
        ("$ whoami", MINT, 0.4, 0.7),
        ("Soumava Paul", INK, 1.3, 0.9),
        ("$ cat about.md", MINT, 2.6, 0.9),
        ("Full-stack developer. I build products end to end:", INK, 3.7, 2.2),
        ("the API, the web app and the native app.", INK, 6.0, 1.8),
        ("$ stack --list", MINT, 8.3, 0.9),
        ("TypeScript  React  Expo  FastAPI  Postgres  Python", AMBER, 9.4, 2.2),
        ("$ status", MINT, 12.0, 0.6),
        ("open to full-stack roles", INK, 12.8, 1.2),
    ]
    css, body = [], []
    x0, y0, lh = 28, 72, 25
    for i, (t, col, st, dur) in enumerate(lines):
        y = y0 + i * lh
        w = len(t) * CW + 8
        a, b = st / LOOP * 100, (st + dur) / LOOP * 100
        # A panel-coloured cover slides right in steps, revealing one char at a time.
        css.append(
            f"@keyframes t{i}{{0%,{a:.3f}%{{transform:translateX(-{w:.1f}px)}}"
            f"{b:.3f}%,97%{{transform:translateX(0)}}100%{{transform:translateX(-{w:.1f}px)}}}}"
            f".t{i}{{animation:t{i} {LOOP}s steps({len(t)},end) infinite}}")
        body.append(f'<text x="{x0}" y="{y}" fill="{col}" font-size="13" xml:space="preserve">{esc(t)}</text>')
        body.append(f'<rect class="t{i}" x="{x0 - 2 + w:.1f}" y="{y - 15}" width="{w:.1f}" height="21" fill="{PANEL}"/>')

    # Blinking cursor after the last line.
    # Hidden while typing; blinks every 0.5 s once the last line is done; hidden again at loop reset.
    done = lines[-1][2] + lines[-1][3] + 0.2
    frames, t, on = ["0%{opacity:0}"], done, True
    while t < LOOP * 0.97 - 0.05:
        frames.append(f"{t / LOOP * 100:.3f}%{{opacity:{1 if on else 0}}}")
        t, on = t + 0.5, not on
    frames.append("97%,100%{opacity:0}")
    css.append(f"@keyframes bl{{{''.join(frames)}}}.bl{{animation:bl {LOOP}s steps(1,end) infinite}}")
    cy = y0 + (len(lines) - 1) * lh
    body.append(f'<rect class="bl" x="{x0 + len(lines[-1][0]) * CW + 10:.1f}" y="{cy - 12}" width="8" height="15" fill="{MINT}"/>')

    # Twinkling ASCII stars on the right half, kept clear of the lighthouse.
    random.seed(7)
    for k in range(34):
        sx, sy = random.randint(470, 820), random.randint(48, 340)
        if (560 < sx < 800 and 60 < sy < 300) or 278 < sy < 300:
            continue
        d, dl = random.uniform(1.6, 4.2), random.uniform(0, 4)
        ch = random.choice([".", "*", "+", ".", "."])
        css.append(f".s{k}{{animation:tw {d:.2f}s ease-in-out {dl:.2f}s infinite}}")
        body.append(f'<text class="s{k}" x="{sx}" y="{sy}" fill="{DIM}" font-size="13">{ch}</text>')
    css.append("@keyframes tw{0%,100%{opacity:.12}50%{opacity:.85}}")

    # ASCII lighthouse with a sweeping beam.
    cx, top, FS = 600, 96, 17
    TW = CW * FS / 13
    LH = round(FS * 1.18)
    tower = [
        "     _/\\_     ",
        "    |(  )|    ",
        "    |____|    ",
        "     |  |     ",
        "     |==|     ",
        "     |  |     ",
        "     |==|     ",
        "    /    \\    ",
        "   /______\\   ",
    ]
    spans = "".join(
        f'<tspan x="{cx}" dy="{LH if k else 0}">{esc(l)}</tspan>' for k, l in enumerate(tower))
    lamp_x, lamp_y = cx + 7 * TW, top + LH - 5
    css.append("@keyframes gl{0%,100%{opacity:.35}50%{opacity:1}}.gl{animation:gl 3s ease-in-out infinite}")
    body.append(
        f'<defs><radialGradient id="lg"><stop offset="0" stop-color="{AMBER}" stop-opacity=".55"/>'
        f'<stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></radialGradient></defs>'
        f'<circle class="gl" cx="{lamp_x:.1f}" cy="{lamp_y}" r="30" fill="url(#lg)" opacity=".6"/>')
    body.append(f'<text x="{cx}" y="{top}" fill="{INK}" font-size="{FS}" xml:space="preserve">{spans}</text>')
    # Beam: left, off, right, off — one sweep every 6 s, each ray fading out from the lamp.
    css.append("@keyframes bmL{0%,6%{opacity:0}12%,30%{opacity:1}36%,100%{opacity:0}}.bmL{animation:bmL 6s linear infinite}")
    css.append("@keyframes bmR{0%,56%{opacity:0}62%,80%{opacity:1}86%,100%{opacity:0}}.bmR{animation:bmR 6s linear infinite}")
    ray = "=" * 13
    lx = lamp_x - 3.2 * TW - len(ray) * CW
    rx = lamp_x + 3.2 * TW
    body.append(
        f'<defs><linearGradient id="fl" x1="1" x2="0"><stop offset="0" stop-color="{AMBER}"/>'
        f'<stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="fr"><stop offset="0" stop-color="{AMBER}"/>'
        f'<stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></linearGradient></defs>')
    body.append(f'<text class="bmL" x="{lx:.1f}" y="{lamp_y + 4}" fill="url(#fl)" font-size="13" opacity="0">{ray}</text>')
    body.append(f'<text class="bmR" x="{rx:.1f}" y="{lamp_y + 4}" fill="url(#fr)" font-size="13" opacity="0">{ray}</text>')
    # Water line.
    css.append("@keyframes wv{0%,100%{transform:translateX(0)}50%{transform:translateX(-8px)}}.wv{animation:wv 4s ease-in-out infinite}")
    body.append(f'<text class="wv" x="{cx - 40}" y="{top + LH * 9 + 4}" fill="{MINT}" font-size="13" opacity=".55">'
                f'{"~ " * 21}</text>')

    css.append("@media (prefers-reduced-motion:reduce){*{animation:none!important}}")
    label = ("A terminal window. whoami: Soumava Paul. Full-stack developer who builds products end to end: "
             "the API, the web app and the native app. Stack: TypeScript, React, Expo, FastAPI, Postgres, "
             "Python. Status: open to full-stack roles. Beside it an ASCII lighthouse sweeps its beam.")
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-label="{esc(label)}"><title>Soumava Paul</title>'
        f'<defs><clipPath id="w"><rect x="5" y="2" width="836" height="372" rx="12"/></clipPath></defs>'
        f'<style>text{{font-family:{FONT}}}{"".join(css)}</style>'
        f'<g clip-path="url(#w)"><rect x="5" y="2" width="836" height="372" fill="{PANEL}"/>'
        f'<rect x="5" y="2" width="836" height="32" fill="{BG}"/>'
        f'<circle cx="26" cy="18" r="5.5" fill="#FF5F57"/><circle cx="46" cy="18" r="5.5" fill="#FEBC2E"/>'
        f'<circle cx="66" cy="18" r="5.5" fill="#28C840"/>'
        f'<text x="423" y="22" fill="{DIM}" font-size="12" text-anchor="middle">pixar634 — zsh</text>'
        f'{"".join(body)}</g>'
        f'<rect x="5.5" y="2.5" width="835" height="371" rx="12" fill="none" stroke="{LINE}"/></svg>')
    with open(os.path.join(OUT, "hero.svg"), "w", encoding="utf-8") as f:
        f.write(svg)


ACCENTS = [MINT, AMBER, "#7FB2F0", "#E07A5F", "#B79CF0", MINT]


def tile(slug, name, sub, tag, w, i):
    h = 192
    col = ACCENTS[i % len(ACCENTS)]
    dur = 7 + i * 0.9
    subs = "".join(
        f'<text x="24" y="{112 + k * 19}" fill="{DIM}" font-size="12.5">{esc(s)}</text>'
        for k, s in enumerate(sub))
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{esc(name)}: {esc(" ".join(sub))}"><title>{esc(name)}</title>'
        f'<defs><clipPath id="c"><rect x="5" y="2" width="{w - 10}" height="186" rx="14"/></clipPath>'
        f'<linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{col}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{col}" stop-opacity=".22"/>'
        f'<stop offset="1" stop-color="{col}" stop-opacity="0"/></linearGradient></defs>'
        f'<style>text{{font-family:{FONT}}}'
        f'@keyframes sw{{0%{{transform:translateX(-{w}px)}}55%,100%{{transform:translateX({w}px)}}}}'
        f'.sw{{animation:sw {dur:.1f}s ease-in-out infinite}}'
        f'@keyframes pu{{0%,100%{{opacity:.3}}50%{{opacity:1}}}}.pu{{animation:pu 2.4s ease-in-out infinite}}'
        f'@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.sw{{display:none}}}}</style>'
        f'<g clip-path="url(#c)"><rect x="5" y="2" width="{w - 10}" height="186" fill="{PANEL}"/>'
        f'<rect class="sw" x="5" y="2" width="{w // 2}" height="186" fill="url(#g)"/>'
        f'<rect x="5" y="2" width="3" height="186" fill="{col}"/>'
        f'<circle class="pu" cx="{w - 28}" cy="30" r="4" fill="{col}"/>'
        f'<text x="24" y="36" fill="{col}" font-size="11" letter-spacing="1.5">{esc(tag.upper())}</text>'
        f'<text x="24" y="80" fill="{INK}" font-size="{22 if w > 300 else 19}" font-weight="700">{esc(name)}</text>'
        f'{subs}</g>'
        f'<rect x="5.5" y="2.5" width="{w - 11}" height="185" rx="14" fill="none" stroke="{LINE}"/></svg>')
    with open(os.path.join(OUT, f"tile-{slug}.svg"), "w", encoding="utf-8") as f:
        f.write(svg)


hero()
tile("lighthouse", "Lighthouse", ["Weekend discovery for India.", "letsgolighthouse.co.in"], "founder project", 423, 0)
tile("jobmagnet", "jobmagnet", ["Turn your CV into a hard", "to ignore candidature."], "python · public", 423, 1)
tile("prepster", "prepster", ["AI-powered mock", "interview bot."], "public", 211, 2)
tile("jobtracker", "jobtracker", ["Next.js app.", "Private repo."], "typescript", 211, 3)
tile("yodatrader", "yodatrader", ["Trading research.", "Private repo."], "python", 211, 4)
tile("autoops", "autoops", ["Work in progress.", "Private repo."], "python", 211, 5)
print("ok", sorted(os.listdir(OUT)))
