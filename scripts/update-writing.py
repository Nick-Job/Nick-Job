#!/usr/bin/env python3
"""Regenerate assets/writing.svg from the blog RSS feed.

Design: dark card matching the profile's other cards; latest 5 posts,
date on the left, title on the right, thin dividers between rows.
Usage: python3 scripts/update-writing.py
Writes assets/writing.svg in the repository root.
"""
import os
import re
import urllib.request
import xml.etree.ElementTree as ET

FEED = "https://nick-space-blog.vercel.app/rss.xml"
MAX_POSTS = 5

CJK = "'PingFang SC', 'Microsoft YaHei', 'Segoe UI', sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
MONTHS = {m: i + 1 for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def est_w(s, px):
    return sum(px if ord(ch) > 0x2E7F else px * 0.55 for ch in s)


def trunc(s, limit, px=15):
    if est_w(s, px) <= limit:
        return s
    out = ""
    for ch in s:
        if est_w(out + ch, px) > limit - px:
            break
        out += ch
    return out + "…"


raw = urllib.request.urlopen(FEED).read()
root = ET.fromstring(raw)
items = root.findall("./channel/item")[:MAX_POSTS]

posts = []
for it in items:
    title = it.findtext("title") or ""
    pub = it.findtext("pubDate") or ""
    m = re.search(r"(\d{1,2}) (\w{3}) (\d{4})", pub)
    ds = ""
    if m:
        ds = f"{m.group(3)}.{MONTHS[m.group(2)]:02d}.{int(m.group(1)):02d}"
    posts.append((ds, title))

rows, dividers = [], []
TOP, RH = 24, 56
for i, (ds, title) in enumerate(posts):
    yb = TOP + i * RH + 35
    rows.append(f'<text x="56" y="{yb}" font-family="{MONO}" font-size="12.5" fill="#7d8aa0">{ds}</text>')
    rows.append(f'<text x="196" y="{yb}" font-family="{CJK}" font-size="15" font-weight="500" fill="#ffffff">{esc(trunc(title, 600))}</text>')
    if i > 0:
        dividers.append(f'<line x1="56" y1="{TOP + i * RH}" x2="824" y2="{TOP + i * RH}" stroke="#ffffff" stroke-opacity="0.08"/>')
H = TOP + len(posts) * RH + 24

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 {H}" width="880" height="{H}" role="img" aria-label="Latest writing">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b1220"/>
      <stop offset="55%" stop-color="#101827"/>
      <stop offset="100%" stop-color="#171233"/>
    </linearGradient>
  </defs>
  <rect x="0" y="0" width="880" height="{H}" rx="24" fill="url(#bg)"/>
  <rect x="0" y="0" width="880" height="{H}" rx="24" fill="none" stroke="#ffffff" stroke-opacity="0.08"/>
  {''.join(dividers)}
  {''.join(rows)}
</svg>
"""

os.makedirs("assets", exist_ok=True)
with open("assets/writing.svg", "w") as f:
    f.write(svg)
print(f"OK: assets/writing.svg ({len(posts)} posts)")
