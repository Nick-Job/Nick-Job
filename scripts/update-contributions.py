#!/usr/bin/env python3
"""Regenerate assets/contributions.svg from GitHub contribution data.

Design: dark card, last 26 weeks as gradient bars (no empty grid cells).
Usage: GH_TOKEN=<token> python3 scripts/update-contributions.py
Writes assets/contributions.svg in the repository root.
"""
import json
import os
import urllib.request
from datetime import date

TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
if not TOKEN:
    raise SystemExit("GH_TOKEN/GITHUB_TOKEN is required")

QUERY = """query {
  user(login: "Nick-Job") {
    contributionsCollection {
      contributionCalendar {
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}"""

req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": QUERY}).encode(),
    headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
)
cal = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
all_weeks = cal["weeks"]

# Aggregate each GitHub week (Sunday start) and keep the last 26.
weekly = []
for week in all_weeks:
    days = week["contributionDays"]
    if not days:
        continue
    weekly.append((date.fromisoformat(days[0]["date"]), sum(d["contributionCount"] for d in days)))
weekly = weekly[-26:]
total = sum(v for _, v in weekly)
vmax = max((v for _, v in weekly), default=0) or 1

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
X0, X1, BASE, MAXH = 56, 824, 204, 120
slot = (X1 - X0) / len(weekly)
BW = 17

bars, labels, peaks = [], [], []
last_month = None
for i, (sun, v) in enumerate(weekly):
    cx = X0 + i * slot + slot / 2
    x = cx - BW / 2
    if v == 0:
        bars.append(f'<rect x="{x:.1f}" y="{BASE - 4}" width="{BW}" height="4" rx="2" fill="url(#spectrum)" opacity="0.22"/>')
    else:
        h = max(6, round(v / vmax * MAXH))
        bars.append(f'<rect x="{x:.1f}" y="{BASE - h}" width="{BW}" height="{h}" rx="4" fill="url(#spectrum)"/>')
        if v == vmax:
            peaks.append(f'<text x="{cx:.1f}" y="{BASE - h - 10}" text-anchor="middle" font-family="{MONO}" font-size="11.5" fill="#c9d4e3">{v}</text>')
    if sun.month != last_month:
        last_month = sun.month
        labels.append(f'<text x="{cx:.1f}" y="230" text-anchor="middle" font-family="{MONO}" font-size="10.5" fill="#5f7089">{sun.strftime("%b")}</text>')

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 252" width="880" height="252" role="img" aria-label="Contributions in the last 26 weeks">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b1220"/>
      <stop offset="55%" stop-color="#101827"/>
      <stop offset="100%" stop-color="#171233"/>
    </linearGradient>
    <linearGradient id="spectrum" gradientUnits="userSpaceOnUse" x1="{X0}" y1="0" x2="{X1}" y2="0">
      <stop offset="0%" stop-color="#0a84ff"/>
      <stop offset="50%" stop-color="#bf5af2"/>
      <stop offset="100%" stop-color="#ff375f"/>
    </linearGradient>
  </defs>
  <rect x="0" y="0" width="880" height="252" rx="24" fill="url(#bg)"/>
  <rect x="0" y="0" width="880" height="252" rx="24" fill="none" stroke="#ffffff" stroke-opacity="0.08"/>
  <text x="56" y="46" font-family="{MONO}" font-size="12" letter-spacing="3" fill="#8ab6ff">CONTRIBUTIONS · LAST 26 WEEKS</text>
  <text x="824" y="46" text-anchor="end" font-family="{MONO}" font-size="13" fill="#c9d4e3">{total} total</text>
  {''.join(peaks)}
  {''.join(bars)}
  <line x1="{X0}" y1="{BASE}" x2="{X1}" y2="{BASE}" stroke="#ffffff" stroke-opacity="0.14"/>
  {''.join(labels)}
</svg>
"""

os.makedirs("assets", exist_ok=True)
with open("assets/contributions.svg", "w") as f:
    f.write(svg)
print(f"OK: assets/contributions.svg ({len(weekly)} weeks, total {total})")
