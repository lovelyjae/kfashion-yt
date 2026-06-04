#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""쇼츠 썸네일 10종 HTML 생성기 (1080x1920). chrome 헤드리스로 PNG 변환."""
import os

OUT = os.path.dirname(os.path.abspath(__file__))

# (파일명, 상단 작은 라벨, 메인 큰 카피[줄들], 서브 카피, 강조색A, 강조색B, 배경 그라데이션, 이모지/뱃지)
THUMBS = [
    ("01_haul",      "MUSINSA HAUL", ["EVERYTHING", "UNDER", "$30"], "8 pieces · Seoul",
     "#fbbf24", "#ec4899", "#1a1033,#3b0764", "🛍️"),
    ("02_price",     "PRICE SHOCK",  ["40% CHEAPER", "IN KOREA"], "Same brand · half price",
     "#34d399", "#22d3ee", "#06281f,#064e3b", "🇰🇷"),
    ("03_thrift",    "SEOUL THRIFT", ["INSANE", "THRIFT", "FROM $5"], "Dongmyo · Gwangjang",
     "#fbbf24", "#f97316", "#231400,#451a03", "♻️"),
    ("04_lookbook",  "STREET 2026",  ["HOW SEOUL", "GEN-Z", "DRESS"], "Acubi · oversized · muted",
     "#c4b5fd", "#8b5cf6", "#160f2e,#2e1065", "👟"),
    ("05_idols",     "IDOL'S PICK",  ["WHERE", "IDOLS", "SHOP"], "Seongsu · under $50",
     "#f9a8d4", "#ec4899", "#2a0a1e,#500724", "✨"),
    ("06_acubi",     "ACUBI 101",    ["ACUBI", "STYLE", "EXPLAINED"], "+ where to buy",
     "#a78bfa", "#6366f1", "#0f1033,#1e1b4b", "🤍"),
    ("07_hongdae",   "HONGDAE GUIDE",["DON'T GO TO", "HONGDAE", "WITHOUT THIS"], "Skip the tourist traps",
     "#f87171", "#ef4444", "#2a0808,#450a0a", "❌"),
    ("08_taxrefund", "MONEY HACK",   ["SAVE 10%", "EVERY TIME"], "Tourist tax refund",
     "#34d399", "#10b981", "#06281f,#022c22", "💸"),
    ("09_grwm",      "GRWM",         ["SEOUL", "CAFÉ DATE", "FIT"], "Done in 5 min",
     "#fcd34d", "#fb7185", "#2a1810,#431407", "☕"),
    ("10_seongsu",   "SHOP MAP",     ["SEONGSU =", "BROOKLYN", "OF SEOUL"], "Walkable route",
     "#5eead4", "#14b8a6", "#04201c,#134e4a", "📍"),
]

PAGE = """<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden}}
.t{{width:1080px;height:1920px;position:relative;
  background:linear-gradient(160deg,{bg});
  font-family:'Arial Black','Apple SD Gothic Neo',sans-serif;
  display:flex;flex-direction:column;justify-content:center;padding:90px 80px}}
.t::before{{content:"";position:absolute;top:-200px;right:-200px;width:900px;height:900px;
  background:radial-gradient(circle,{a}55,transparent 60%);}}
.t::after{{content:"";position:absolute;bottom:-260px;left:-220px;width:820px;height:820px;
  background:radial-gradient(circle,{b}44,transparent 62%);}}
.label{{position:absolute;top:90px;left:80px;display:flex;align-items:center;gap:18px;z-index:3}}
.label .bar{{width:60px;height:10px;background:{a};border-radius:6px}}
.label span{{color:{a};font-size:42px;font-weight:900;letter-spacing:4px}}
.emoji{{position:absolute;top:74px;right:80px;font-size:120px;z-index:3;
  font-family:'Apple Color Emoji',sans-serif}}
.main{{position:relative;z-index:3}}
.main .line{{font-size:118px;font-weight:900;line-height:1.02;color:#fff;
  letter-spacing:-3px;text-shadow:0 8px 30px rgba(0,0,0,.6);white-space:nowrap}}
.main .line.hl{{color:{a}}}
.main .line.hl2{{color:{b}}}
.sub{{position:relative;z-index:3;margin-top:54px;font-size:60px;font-weight:900;
  color:#fff;background:{a};display:inline-block;padding:20px 40px;border-radius:22px;
  align-self:flex-start;letter-spacing:1px;
  font-family:'Apple SD Gothic Neo','Arial Black',sans-serif}}
.brand{{position:absolute;bottom:80px;left:80px;z-index:3;color:#ffffffcc;
  font-size:40px;font-weight:900;letter-spacing:3px}}
.save{{position:absolute;bottom:74px;right:80px;z-index:3;color:#fff;font-size:46px;
  font-weight:900;background:#ffffff22;border:4px solid #ffffff55;border-radius:999px;
  padding:16px 36px;font-family:'Apple SD Gothic Neo','Arial Black',sans-serif}}
</style></head><body>
<div class="t">
  <div class="label"><div class="bar"></div><span>{label}</span></div>
  <div class="emoji">{emoji}</div>
  <div class="main">{lines}</div>
  <div class="sub">{sub}</div>
  <div class="brand">@SHOP IN SEOUL</div>
  <div class="save">SAVE 🔖</div>
</div></body></html>"""

def render_lines(lines, a_cls, b_cls):
    # 가운데 줄을 강조색으로
    out = []
    n = len(lines)
    for i, ln in enumerate(lines):
        cls = "line"
        if n == 3 and i == 2:
            cls = "line hl"
        elif n == 3 and i == 1:
            cls = "line hl2"
        elif n == 2 and i == 1:
            cls = "line hl"
        out.append(f'<div class="{cls}">{ln}</div>')
    return "".join(out)

for fn, label, lines, sub, a, b, bg, emoji in THUMBS:
    html = PAGE.format(bg=bg, a=a, b=b, label=label,
                       lines=render_lines(lines, a, b), sub=sub, emoji=emoji)
    with open(os.path.join(OUT, fn + ".html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", fn + ".html")
print("DONE", len(THUMBS))
