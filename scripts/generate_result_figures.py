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
        marker(60, 166, "orange", True), text(77, 173, "CEM", 18),
        marker(150, 166, "forest"), text(167, 173, "Agentic search", 18),
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
    values = "; ".join(f'{c["category"]}, {c["tasks"]} tasks: CEM {c["arms"]["A0"]["search_cost"]["mean_search_rollouts_per_task"]:.3f}, Agentic search {c["arms"]["L3P"]["search_cost"]["mean_search_rollouts_per_task"]:.3f}' if search else f'{c["category"]}, {c["tasks"]} tasks: CEM {c["arms"]["A0"]["display_percent"]}, Agentic search {c["arms"]["L3P"]["display_percent"]}' for c in data["categories"])
    description = subtitle + ". " + values + ". " + (data["search_cost_definition"] if search else data["metric"])
    return svg(810, title, description, p)


def curriculum_chart(data):
    p = [
        text(50, 44, "ADROIT  /  GPT-6 ASTRA", 16, "forest", letter_spacing=2),
        text(50, 91, "A contrast between two training protocols", 33, serif=True),
        text(50, 126, "Final held-out outcomes · one chain per task and protocol · 30 episodes each", 20, "muted"),
        marker(60, 169, "orange", True), text(77, 176, "Fixed starts (Agentic search)", 19),
        marker(505, 169, "forest"), text(522, 176, "Fresh random starts (Agentic search)", 19),
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


def comparison_chart(data):
    title = "Three search treatments, one task set"
    subtitle = f'Mean held-out success · {data["subset"]} · unaccepted tasks count as zero'
    arms = (("CEM", "orange", "square"), ("Agentic search", "forest", "circle"), ("Agentic + grasp", "ink", "diamond"))

    def mark(x, y, color, shape):
        if shape == "diamond":
            return f'<rect x="{x - 5}" y="{y - 5}" width="10" height="10" fill="{PALETTE[color]}" transform="rotate(45 {x} {y})"/>'
        return marker(x, y, color, shape == "square")

    overall = data["overall_mean_percent"]
    p = [
        text(50, 44, "DEXVERSE  /  CLAUDE OPUS 5.5", 16, "forest", letter_spacing=2),
        text(50, 91, title, 33, serif=True),
        text(50, 126, subtitle, 20, "muted"),
        text(1050, 173, "success (%)", 16, "muted", "end"),
    ]
    lx = 60
    for name, color, shape in arms:
        label = f"{name} · {overall[name]:.1f}"
        p += [mark(lx, 166, color, shape), text(lx + 17, 173, label, 18)]
        lx += 52 + 10 * len(label)
    x0, x1 = 270, 930
    x = lambda value: x0 + (x1 - x0) * value / 100
    pitch, y0 = 78, 238
    bottom = y0 + pitch * len(data["categories"]) - 30
    for tick in (0, 25, 50, 75, 100):
        p.append(line(x(tick), 203, x(tick), bottom))
        p.append(text(x(tick), bottom + 33, str(tick), 17, "muted", "middle"))
    for i, category in enumerate(data["categories"]):
        y = y0 + i * pitch
        p.append(text(50, y, category["category"], 24, serif=True))
        p.append(text(50, y + 25, f'{category["tasks"]} tasks', 17, "muted"))
        for (name, color, shape), dy in zip(arms, (-16, 2, 20)):
            value = category["arms"][name]["mean_heldout_percent"]
            p.append(line(x0, y + dy, x(value), y + dy, color, 2))
            p.append(mark(x(value), y + dy, color, shape))
            p.append(text(1050, y + dy + 6, f"{value:.1f}", 18, color, "end"))
    foot = bottom + 68
    p.extend([
        text((x0 + x1) / 2, foot, "Mean held-out success rate (%)", 20, "muted", "middle"),
        line(50, foot + 29, 1050, foot + 29),
        text(50, foot + 65, "Agentic + grasp adds a fixed prompt asking for a grasp-aware controller; it lowers Long-horizon most.", 19),
        text(50, foot + 96, "Each accepted policy is tested twice on the same 50 unseen starts. One training chain per task and arm.", 18, "muted"),
    ])
    values = "; ".join(f'{c["category"]} ({c["tasks"]} tasks): ' + ", ".join(f'{n} {c["arms"][n]["mean_heldout_percent"]}%' for n, _, _ in arms) for c in data["categories"])
    return svg(foot + 130, title, f"{subtitle}. {values}. {data['metric']}", p)


def search_comparison_chart(data, rollouts=False):
    """Figure 6 (rollouts) and the retired held-out chart: Agentic search vs. CEM search per Adroit task and DexVerse category."""
    title = "Total rollouts to an accepted policy" if rollouts else "Held-out success of the frozen policy"
    subtitle = ("Parameter-search rollouts + policy-design resets · DexVerse: mean per task" if rollouts
                else "Unseen starts · DexVerse: mean per task, unaccepted tasks count as zero")
    reset_color = "#8db3a3"
    arms = [("model_driven", "Agentic search", "forest"), ("cem", "CEM search", "orange")]
    p = [
        text(50, 44, "ADROIT + DEXVERSE  /  CLAUDE OPUS 5.5", 16, "forest", letter_spacing=2),
        text(50, 91, title, 33, serif=True),
        text(50, 126, subtitle, 20, "muted"),
    ]
    legend = [(label, color) for _, label, color in arms]
    if rollouts:
        legend.insert(1, ("Agentic resets", reset_color))
    lx = 50
    for label, color in legend:
        p += [f'<rect x="{lx}" y="158" width="16" height="16" fill="{PALETTE.get(color, color)}"/>', text(lx + 24, 172, label, 17)]
        lx += 48 + 9 * len(label)
    adroit = [g for g in data["summary"] if g["group"] == "Adroit"]
    dex = [g for g in data["summary"] if g["group"] != "Adroit"]
    panels = [("ADROIT", [(g["task"], "30 unseen starts", g) for g in adroit], 1500 if rollouts else 100),
              ("DEXVERSE", [(g["group"], f'{g["tasks"]} tasks', g) for g in dex], 600 if rollouts else 100)]
    x0, x1, bar, pitch = 270, 960, 15, 62
    y = 222
    fmt_total = lambda v: f"{v:,.0f}" if float(v).is_integer() else f"{v:,.1f}"
    for name, rows, xmax in panels:
        x = lambda v, xmax=xmax: x0 + (x1 - x0) * min(v, xmax) / xmax
        p.append(text(50, y, name, 15, "forest", letter_spacing=2))
        top = y + 14
        bottom = top + pitch * len(rows)
        ticks = range(0, xmax + 1, 300 if xmax == 1500 else (100 if rollouts else 20))
        for t in ticks:
            p.append(line(x(t), top, x(t), bottom))
            p.append(text(x(t), bottom + 26, f"{t:,}" + ("" if rollouts else "%"), 15, "muted", "middle"))
        for i, (label, sub, g) in enumerate(rows):
            cy = top + 16 + i * pitch
            p.append(text(50, cy + 14, label, 22, serif=True))
            p.append(text(50, cy + 38, sub, 15, "muted"))
            for j, (key, _, color) in enumerate(arms):
                by = cy + j * (bar + 4)
                value = g[key]
                if rollouts:
                    total = value["total_rollouts"]
                    if key == "model_driven":
                        p.append(f'<rect x="{x0}" y="{by}" width="{x(value["search_rollouts"]) - x0:.1f}" height="{bar}" fill="{PALETTE[color]}"/>')
                        p.append(f'<rect x="{x(value["search_rollouts"]):.1f}" y="{by}" width="{x(total) - x(value["search_rollouts"]):.1f}" height="{bar}" fill="{reset_color}"/>')
                    else:
                        p.append(f'<rect x="{x0}" y="{by}" width="{x(total) - x0:.1f}" height="{bar}" fill="{PALETTE[color]}"/>')
                    label_text = f'{fmt_total(total)}  ({fmt_total(value["search_rollouts"])} + {fmt_total(value["resets"])})'
                    p.append(text(x(total) + 8, by + 12, label_text, 14, "ink"))
                else:
                    v = value["heldout_percent"]
                    p.append(f'<rect x="{x0}" y="{by}" width="{x(v) - x0:.1f}" height="{bar}" fill="{PALETTE[color]}"/>')
                    p.append(text(x(v) + 8, by + 12, f"{v:.1f}%", 14, "ink"))
        y = bottom + 74
    foot = y - 20
    note = ("Labels: total (search + resets). Resets are policy-design restarts; CEM search bars combine both counters." if rollouts
            else "Adroit: one run on 30 unseen starts. DexVerse: 50 unseen starts, two repeats averaged.")
    p.extend([
        line(50, foot, 1050, foot),
        text(50, foot + 34, note, 18),
        text(50, foot + 62, "One training chain per task and arm. Adroit Pen and DexVerse Long-horizon are in Section 4.", 17, "muted"),
    ])
    key = "total_rollouts" if rollouts else "heldout_percent"
    values = "; ".join(f'{g.get("task", g["group"]) if g["group"] == "Adroit" else g["group"]}: Agentic search {g["model_driven"][key]}, CEM search {g["cem"][key]}'
                       for g in data["summary"])
    return svg(foot + 92, title, f"{subtitle}. {values}.", p)


def main():
    dexverse = json.loads((ROOT / "assets/data/dexverse-results.json").read_text())
    adroit = json.loads((ROOT / "assets/data/adroit-curriculum.json").read_text())
    comparison = json.loads((ROOT / "assets/data/dexverse-comparison-e2.json").read_text())
    tasks = json.loads((ROOT / "assets/data/search-results-by-task.json").read_text())
    outputs = {
        "dexverse-comparison-e2.svg": comparison_chart(comparison),
        "evidence-heldout.svg": search_comparison_chart(tasks),
        "evidence-rollouts.svg": search_comparison_chart(tasks, rollouts=True),
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
