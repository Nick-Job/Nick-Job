#!/usr/bin/env python3
"""Regenerate assets/contributions.svg from GitHub contribution data.

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
weeks = cal["weeks"]

# --- layout ---------------------------------------------------------------
CELL, GAP, PAD = 11, 3, 14
W = len(weeks)
H = 7
width = W * (CELL + GAP) + PAD * 2 - GAP
height = H * (CELL + GAP) + PAD * 2 - GAP


def row_of(day_str):
    """GitHub calendar rows: Sunday=0 .. Saturday=6."""
    return (date.fromisoformat(day_str).weekday() + 1) % 7


def intensity(count):
    if count == 0:
        return None
    if count >= 10:
        return 0.95
    if count >= 5:
        return 0.70
    if count >= 3:
        return 0.50
    return 0.30


cells = []
for w_i, week in enumerate(weeks):
    for day in week["contributionDays"]:
        x = PAD + w_i * (CELL + GAP)
        y = PAD + row_of(day["date"]) * (CELL + GAP)
        a = intensity(day["contributionCount"])
        if a is None:
            cells.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" '
                f'fill="none" stroke="rgba(128,128,128,0.18)" stroke-width="1"/>'
            )
        else:
            cells.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" '
                f'fill="rgba(10,132,255,{a})"/>'
            )

svg = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
    'role="img" aria-label="Nick\u2019s contributions in the last year">\n'
    "  %s\n"
    "</svg>\n"
) % (width, height, width, height, "\n  ".join(cells))

os.makedirs("assets", exist_ok=True)
with open("assets/contributions.svg", "w") as f:
    f.write(svg)
print(f"OK: assets/contributions.svg ({len(cells)} cells, {width}x{height})")
