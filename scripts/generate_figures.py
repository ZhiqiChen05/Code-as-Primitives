#!/usr/bin/env python3
"""Regenerate the blog's original SVG figures using Python's standard library.

Run from anywhere: PYTHONDONTWRITEBYTECODE=1 python3 scripts/generate_figures.py
Data are transcribed from the audited report recorded in docs/figure-sources.json.
No source repositories, external packages, or network access are required to run.
"""

from html import escape
import json
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "figures"
PALETTE = {
    "paper": "#f6f3eb",
    "ink": "#242620",
    "forest": "#276451",
    "orange": "#be5d39",
    "border": "#d7d6ca",
    "muted": "#63675d",
    "wash": "#e8eee5",
}


def text(x, y, value, size=20, fill="ink", anchor="start", serif=False, **attrs):
    font = "Georgia, 'Times New Roman', serif" if serif else "Arial, Helvetica, sans-serif"
    extra = " ".join(f'{k.replace("_", "-")}="{escape(str(v), quote=True)}"' for k, v in attrs.items())
    return f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" fill="{PALETTE.get(fill, fill)}" text-anchor="{anchor}" {extra}>{escape(value)}</text>'


def rect(x, y, width, height, fill="paper", stroke="border", radius=8):
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" fill="{PALETTE[fill]}" stroke="{PALETTE[stroke]}" stroke-width="1.4"/>'


def line(x1, y1, x2, y2, color="border", width=1.4, **attrs):
    extra = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{PALETTE[color]}" stroke-width="{width}" {extra}/>'


def svg(height, title, description, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="{height}" viewBox="0 0 1100 {height}" role="img" aria-labelledby="figure-title figure-desc">
<title id="figure-title">{escape(title)}</title>
<desc id="figure-desc">{escape(description)}</desc>
<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto" markerUnits="userSpaceOnUse"><path d="M 0 0 L 8 4 L 0 8 Z" fill="{PALETTE['forest']}"/></marker></defs>
<rect width="1100" height="{height}" fill="{PALETTE['paper']}"/>
{chr(10).join(body)}
</svg>
'''


def overview():
    p = [
        text(50, 46, "01  /  LEARNING", 16, "forest", letter_spacing=2),
        text(50, 86, "The model writes the controller.", 32, serif=True),
        rect(50, 130, 250, 132),
        rect(425, 130, 250, 132, "wash", "forest"),
        rect(800, 130, 250, 132),
        text(175, 177, "Frontier model", 25, anchor="middle", serif=True),
        text(175, 211, "Reason about the task", 18, "muted", "middle"),
        text(175, 238, "Design and revise code", 18, "muted", "middle"),
        text(550, 177, "Python policy", 25, "forest", "middle", True),
        text(550, 211, "policy.py + PARAMS", 20, "forest", "middle"),
        text(550, 238, "Logic + tunable numbers", 18, "muted", "middle"),
        text(925, 177, "Simulator", 25, anchor="middle", serif=True),
        text(925, 211, "Execute native actions", 18, "muted", "middle"),
        text(925, 238, "Collect task feedback", 18, "muted", "middle"),
        line(312, 199, 413, 199, "forest", 2, marker_end="url(#arrow)"),
        text(362, 185, "write / revise", 16, "forest", "middle"),
        line(687, 199, 788, 199, "forest", 2, marker_end="url(#arrow)"),
        text(737, 185, "roll out", 16, "forest", "middle"),
        f'<path d="M 925 276 V 311 H 175 V 276" fill="none" stroke="{PALETTE["forest"]}" stroke-width="2" marker-end="url(#arrow)"/>',
        f'<rect x="340" y="294" width="420" height="32" fill="{PALETTE["paper"]}"/>',
        text(550, 316, "Inspect trajectories, scores, and errors", 19, "forest", "middle"),
        rect(50, 355, 1000, 63),
        text(73, 394, "Optional tools", 20, serif=True),
        line(230, 370, 230, 403),
        text(252, 394, "Batched parameter search", 19),
        text(535, 394, "+", 20, "muted"),
        text(578, 394, "NumPy / SciPy analysis", 19),
        text(1027, 394, "during learning", 16, "muted", "end"),
        line(50, 455, 1050, 455),
        text(50, 498, "02  /  DEPLOYMENT", 16, "forest", letter_spacing=2),
        text(1050, 498, "Selected policy is frozen. No model calls.", 19, "forest", "end"),
        rect(50, 539, 250, 105),
        rect(425, 539, 250, 105, "wash", "forest"),
        rect(800, 539, 250, 105),
        text(175, 581, "State observation", 23, anchor="middle", serif=True),
        text(175, 614, "Read the current state", 18, "muted", "middle"),
        text(550, 581, "Frozen Python policy", 20, "forest", "middle", True),
        text(550, 614, "Execute feedback rules", 18, "muted", "middle"),
        text(925, 581, "Actuator targets", 23, anchor="middle", serif=True),
        text(925, 614, "Native low-level control", 18, "muted", "middle"),
        line(312, 592, 413, 592, "forest", 2, marker_end="url(#arrow)"),
        line(687, 592, 788, 592, "forest", 2, marker_end="url(#arrow)"),
        text(550, 687, "The program runs at every control step; the foundation model does not.", 19, "muted", "middle"),
    ]
    return svg(720, "A model learns to write a controller; a frozen program executes it.",
               "During learning, a foundation model writes and revises policy.py with a PARAMS vector, "
               "executes the policy in a simulator, and inspects trajectories, scores, and errors. "
               "Optional tools support batched parameter search and NumPy/SciPy analysis. "
               "During deployment, a frozen Python policy maps state observations to native actuator targets "
               "at each control step without calls to the foundation model. This figure makes no claim "
               "about the number of simulator interactions required for learning.", p)


def outcomes(data):
    p = [
        text(50, 46, "ADROIT  /  FROZEN-POLICY EVALUATION", 16, "forest", letter_spacing=2),
        text(50, 92, "119 successes in 120 held-out episodes", 34, serif=True),
        text(50, 126, "30 unseen starts per task · one training chain per task", 20, "muted"),
        text(50, 179, "TASK", 16, "muted", letter_spacing=1),
        text(1050, 179, "SUCCESSES", 16, "muted", "end", letter_spacing=1),
    ]
    x0, x1 = 235, 900
    x = lambda percentage: x0 + (x1 - x0) * percentage / 100
    for tick in (0, 25, 50, 75, 100):
        p.append(line(x(tick), 199, x(tick), 438))
        p.append(text(x(tick), 469, str(tick), 17, "muted", "middle"))
    for i, row in enumerate(data):
        y = 222 + 66 * i
        color = "orange" if row["successes"] < row["episodes"] else "forest"
        p.extend([
            text(50, y + 7, row["task"], 25, serif=True),
            line(x0, y, x1, y, "border", 1, stroke_dasharray="3 5"),
            line(x(row["wilson_95_percent"][0]), y, x(row["wilson_95_percent"][1]), y, color, 3),
            line(x(row["wilson_95_percent"][0]), y - 8, x(row["wilson_95_percent"][0]), y + 8, color, 2),
            line(x(row["wilson_95_percent"][1]), y - 8, x(row["wilson_95_percent"][1]), y + 8, color, 2),
            f'<circle cx="{x(100 * row["successes"] / row["episodes"])}" cy="{y}" r="7" fill="{PALETTE[color]}" stroke="{PALETTE["paper"]}" stroke-width="2"/>',
            text(1050, y + 7, f'{row["successes"]} / {row["episodes"]}', 24, color, "end"),
        ])
    p.extend([
        text((x0 + x1) / 2, 508, "Held-out success rate (%)", 20, "muted", "middle"),
        line(50, 544, 1050, 544),
        line(52, 579, 100, 579, "forest", 3),
        f'<circle cx="76" cy="579" r="6" fill="{PALETTE["forest"]}" stroke="{PALETTE["paper"]}" stroke-width="2"/>',
        text(116, 585, "Point: observed rate. Whisker: 95% Wilson interval over held-out seeds.", 19),
        text(50, 620, "Intervals describe these frozen policies, not variability across independent training runs.", 18, "muted"),
    ])
    return svg(650, "Adroit frozen policies succeeded in 119 of 120 held-out episodes.",
               "Door: 29 of 30 episodes, 96.7 percent success, 95 percent Wilson interval 83.3 to 99.4 percent. "
               "Hammer, Pen, and Relocate: 30 of 30 episodes each, 100 percent success, interval 88.6 to 100.0 percent. "
               "The horizontal success-rate axis spans 0 to 100 percent. There was one training chain per task. "
               "Intervals quantify variation across held-out seeds for each frozen policy, not independent training runs. "
               "Source: the adroit_seq10_l3pr campaign report.", p)


def main():
    manifest = json.loads((ROOT / "docs" / "figure-sources.json").read_text())
    data = manifest["figures"]["adroit-heldout.svg"]["data"]
    assert sum(row["successes"] for row in data) == 119
    assert sum(row["episodes"] for row in data) == 120
    OUT.mkdir(parents=True, exist_ok=True)
    for name, contents in {"method-overview.svg": overview(), "adroit-heldout.svg": outcomes(data)}.items():
        ET.fromstring(contents)
        (OUT / name).write_text(contents)
        print(f"Generated {OUT / name}")


if __name__ == "__main__":
    main()
