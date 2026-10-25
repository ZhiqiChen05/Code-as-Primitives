#!/usr/bin/env python3
"""Export per-task results for Figures 1 and 4-6 to assets/data/search-results-by-task.json.

The page calls the two campaigns model-driven search (campaign L3PG) and CEM search (campaign A0).

Reads the same campaign reports as DexVerse/docs/figs/l3pg_dexverse_adroit/make_baseline_figures.py
(heldout_success_main.png, total_rollouts_main.png) and copies the L3PG held-out success videos
from DexVerse/docs/videos/l3pg_heldout_success unchanged. Adroit Pen and DexVerse Long-horizon are
left out (Section 4). Needs the source checkouts; run with the CaP-X venv, which has matplotlib:

  /home/djengof/CaP-X/cap-x/.venv/bin/python -I scripts/export_search_tasks.py
"""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIGS = Path("/home/djengof/DexVerse/docs/figs/l3pg_dexverse_adroit")
VIDEOS = Path("/home/djengof/DexVerse/docs/videos/l3pg_heldout_success")
sys.path.insert(0, str(FIGS))
from make_baseline_figures import A0_ADROIT, A0_DEX, BASELINE  # noqa: E402
import make_figures  # noqa: E402
from make_figures import CATEGORIES, DEX_REPORT, HOME, by_category, load_adroit, load_dexverse, rate  # noqa: E402

SKIP = {"Pen", "Long-horizon"}


def a0_tasks():
    out = {}
    for task, campaign in A0_ADROIT.items():
        chain = next(c for c in json.loads((HOME / campaign / "report.json").read_text())["chains"]
                     if c["task"] == task.lower())
        costs, episodes = chain["stages"][0]["costs"], chain["heldout"]["episodes"]
        out[task] = dict(group="Adroit", accepted=chain["stages"][0]["status"] == "success",
                         search=costs["search_rollouts"], resets=costs["reset_count"],
                         rate=100 * sum(e["success"] for e in episodes) / len(episodes))
    category = {}
    for line in DEX_REPORT.read_text().split("## All tasks")[1].splitlines():
        m = re.match(r"\| (%s) \| ([\w-]+) \|" % "|".join(CATEGORIES), line)
        if m:
            category[m.group(2)] = m.group(1)
    for campaign in A0_DEX:
        for chain in json.loads((campaign / "report.json").read_text())["chains"]:
            task = chain["task"].removeprefix("Dexverse-").removesuffix("-v0")
            if task not in category:
                continue
            state = json.loads((campaign / "chains" / chain["key"] / "stage_01/state.json").read_text())
            r = dict(group=category[task], accepted=chain["accepted"], search=chain["search_rollouts"],
                     resets=state["reset_count"], heldout=chain["heldout_repeats"] if chain["accepted"] else None, n=50)
            r["rate"] = rate(r)
            out[task] = r
    return out


def arm(r):
    return dict(accepted=bool(r["accepted"]), search_rollouts=r["search"], resets=r["resets"],
                total_rollouts=r["search"] + r["resets"], heldout_percent=round(rate(r), 1))


def summary(r):
    return dict(search_rollouts=round(r["search"], 1), resets=round(r["resets"], 1),
                total_rollouts=round(r["search"] + r["resets"], 1), heldout_percent=round(rate(r), 1))


def main():
    adroit, dex, a0 = load_adroit(), load_dexverse(), a0_tasks()
    (ROOT / "assets/videos/model-driven").mkdir(parents=True, exist_ok=True)
    tasks = []
    for r in adroit + dex:
        group = r["group"]
        if r["task"] in SKIP or group in SKIP:
            continue
        bench = "Adroit" if group == "Adroit" else "DexVerse"
        src = VIDEOS / f"{bench}-{r['task']}.mp4"
        video = None
        if src.exists():
            video = f"assets/videos/model-driven/{src.name}"
            shutil.copy2(src, ROOT / video)
        tasks.append(dict(benchmark=bench, group=group, task=r["task"], video=video,
                          heldout_repeats=r["heldout"], episodes=r["n"],
                          model_driven=arm(r), cem=arm(a0[r["task"]]), baseline=None))
    groups = [dict(group="Adroit", task=t["task"], model_driven=summary(next(r for r in adroit if r["task"] == t["task"])),
                   cem=summary(a0[t["task"]]), baseline=None) for t in tasks if t["benchmark"] == "Adroit"]
    dex = [r for r in dex if r["group"] not in SKIP]
    make_figures.CATEGORIES = [c for c in CATEGORIES if c not in SKIP]  # by_category divides by task count
    l3_cats = by_category(dex)
    a0_cats = by_category([a0[r["task"]] for r in dex])
    for c, a in zip(l3_cats, a0_cats):
        groups.append(dict(group=c["task"].split(" (")[0], tasks=c["ntasks"], model_driven=summary(c), cem=summary(a),
                           baseline=None))
    data = {
        "model": "claude-opus-5-5",
        "source": "DexVerse campaign report.json files, read by scripts/export_search_tasks.py; videos are the "
                  "recorded held-out success renders, copied unchanged",
        "arms": {"model_driven": "Model-driven search", "cem": "CEM search", "baseline": "Baseline (policy search), not yet run"},
        "heldout_metric": "Adroit: frozen policy on 30 unseen starts, one run. DexVerse: 50 unseen starts, mean of two "
                          "repeats. Unaccepted tasks count as 0%.",
        "rollouts_metric": "Total rollouts = parameter-search rollouts + policy-design resets.",
        "video_note": "One successful model-driven-search held-out episode per task; tasks with no recorded success video show none.",
        "baseline_note": "Baseline values are null until the runs exist; " + ("all BASELINE entries are None"
                         if all(v["rollouts"] is None and v["rate"] is None for v in BASELINE.values()) else "see source"),
        "summary": groups,
        "tasks": tasks,
    }
    (ROOT / "assets/data/search-results-by-task.json").write_text(json.dumps(data, indent=1) + "\n")
    print(len(tasks), "tasks,", sum(t["video"] is not None for t in tasks), "videos")


if __name__ == "__main__":
    main()
