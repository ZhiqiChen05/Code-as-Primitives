#!/usr/bin/env python3
"""Render source-backed result figures from the blog's versioned JSON data.

Uses only the standard library. Run with PYTHONDONTWRITEBYTECODE=1 to avoid caches.
"""

import json
import xml.etree.ElementTree as ET

from generate_figures import ROOT, OUT, PALETTE, text, line, svg


def marker(x, y, color, square=False):
    if square:
        return f'<rect x="{x - 5}" y="{y - 5}" width="10" height="10" fill="{PALETTE[color]}"/>'
    return f'<circle cx="{x}" cy="{y}" r="6" fill="{PALETTE[color]}"/>'


def category_chart(data, search=False):
    title = "Search effort varies across task categories" if search else "Generalization across task categories"
    subtitle = "Mean search rollouts per task · learning and evaluation episodes excluded" if search else "Mean held-out success · 75 valid tasks · unaccepted tasks count as zero"
    p = [
        text(50, 44, "DEXVERSE  /  CLAUDE OPUS 5.5", 16, "forest", letter_spacing=2),
        text(50, 91, title, 33, serif=True),
        text(50, 126, subtitle, 20, "muted"),
        marker(60, 166, "orange", True), text(77, 173, "A0", 18),
        marker(150, 166, "forest"), text(167, 173, "L3+papers", 18),
        text(1050, 173, "mean / task" if search else "success (%)", 16, "muted", "end"),
    ]
    x0, x1 = 270, 930
    maximum = 1500 if search else 100
    x = lambda value: x0 + (x1 - x0) * value / maximum
    ticks = (0, 500, 1000, 1500) if search else (0, 25, 50, 75, 100)
    if search:
        p.append(f'<rect x="{x0}" y="203" width="{x(150) - x0}" height="410" fill="{PALETTE["wash"]}"/>')
        p.append(line(x(150), 203, x(150), 613, "forest", 1.4, stroke_dasharray="5 5"))
        p.append(text(x(150), 196, "150", 16, "forest", "middle"))
    for tick in ticks:
        p.append(line(x(tick), 203, x(tick), 613))
        p.append(text(x(tick), 646, f"{tick:,}", 17, "muted", "middle"))
    for i, category in enumerate(data["categories"]):
        y = 235 + i * 70
        p.append(text(50, y, category["category"], 24, serif=True))
        p.append(text(50, y + 25, f'{category["tasks"]} tasks', 17, "muted"))
        for arm, dy, color, square in (("A0", -9, "orange", True), ("L3P", 14, "forest", False)):
            row = category["arms"][arm]
            value = row["search_cost"]["mean_search_rollouts_per_task"] if search else row["mean_heldout_percent"]
            p.append(line(x0, y + dy, x(value), y + dy, color, 2))
            p.append(marker(x(value), y + dy, color, square))
            p.append(text(1050, y + dy + 6, f"{value:,.1f}", 19, color, "end"))
    p.extend([
        text((x0 + x1) / 2, 681, "Mean search rollouts per task" if search else "Mean held-out success rate (%)", 20, "muted", "middle"),
        line(50, 710, 1050, 710),
        text(50, 746, "Four of six category means are below 150 in each arm." if search else "Each accepted policy is tested twice on the same 50 unseen starts; results are averaged by task.", 19),
        text(50, 777, "A category mean is not a limit on every task. These counts are not total simulator use." if search else "One training chain per task and arm. These are state-observation simulator experiments.", 18, "muted"),
    ])
    values = "; ".join(f'{c["category"]}, {c["tasks"]} tasks: A0 {c["arms"]["A0"]["search_cost"]["mean_search_rollouts_per_task"]:.3f}, L3+papers {c["arms"]["L3P"]["search_cost"]["mean_search_rollouts_per_task"]:.3f}' if search else f'{c["category"]}, {c["tasks"]} tasks: A0 {c["arms"]["A0"]["display_percent"]}, L3+papers {c["arms"]["L3P"]["display_percent"]}' for c in data["categories"])
    description = subtitle + ". " + values + ". " + (data["search_cost_definition"] if search else data["metric"])
    return svg(810, title, description, p)


def curriculum_chart(data):
    p = [
        text(50, 44, "ADROIT  /  GPT-6 ASTRA", 16, "forest", letter_spacing=2),
        text(50, 91, "A contrast between two training protocols", 33, serif=True),
        text(50, 126, "Final held-out outcomes · one chain per task and protocol · 30 episodes each", 20, "muted"),
        marker(60, 169, "orange", True), text(77, 176, "Fixed starts (seq10 L3+papers)", 19),
        marker(505, 169, "forest"), text(522, 176, "Fresh random starts (L3PR)", 19),
        text(1050, 215, "successes", 16, "muted", "end"),
    ]
    x0, x1 = 235, 900
    x = lambda value: x0 + (x1 - x0) * value / 100
    for tick in (0, 25, 50, 75, 100):
        p.append(line(x(tick), 225, x(tick), 530))
        p.append(text(x(tick), 563, str(tick), 17, "muted", "middle"))
    for i, row in enumerate(data["rows"]):
        y = 258 + i * 80
        p.append(text(50, y + 6, row["task"], 25, serif=True))
        for condition, dy, color, square in (("fixed", -11, "orange", True), ("random", 12, "forest", False)):
            r = row[condition]
            value = 100 * r["successes"] / r["episodes"]
            p.append(line(x0, y + dy, x(value), y + dy, color, 2))
            p.append(marker(x(value), y + dy, color, square))
            p.append(text(1050, y + dy + 6, f'{r["successes"]} / {r["episodes"]}', 20, color, "end"))
    p.extend([
        text((x0 + x1) / 2, 601, "Held-out success rate (%)", 20, "muted", "middle"),
        line(50, 633, 1050, 633),
        text(50, 669, "Descriptive comparison: prompts, reset / test seeds, and interaction effort differ.", 19),
        text(50, 700, "These runs do not isolate a causal effect of the curriculum.", 18, "muted"),
    ])
    description = "Final frozen policies after fixed-start versus random-reset sequential learning. " + "; ".join(f'{r["task"]}: fixed {r["fixed"]["successes"]} of 30, random {r["random"]["successes"]} of 30' for r in data["rows"]) + ". Nominal per-stage limits match, but actual interaction cost, prompts, and test seed sets differ. One training chain per condition; this is a descriptive comparison, not a controlled causal ablation. Both protocols increase the evaluation batch size across stages."
    return svg(735, "Adroit outcomes under fixed-start and random-reset training", description, p)


def main():
    dexverse = json.loads((ROOT / "assets/data/dexverse-results.json").read_text())
    adroit = json.loads((ROOT / "assets/data/adroit-curriculum.json").read_text())
    outputs = {
        "dexverse-heldout.svg": category_chart(dexverse),
        "dexverse-search-rollouts.svg": category_chart(dexverse, search=True),
        "adroit-curriculum.svg": curriculum_chart(adroit),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    for name, contents in outputs.items():
        ET.fromstring(contents)
        (OUT / name).write_text(contents)
        print(f"Generated {OUT / name}")


if __name__ == "__main__":
    main()
