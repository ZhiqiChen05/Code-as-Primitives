#!/usr/bin/env python3
"""Export per-task results for Figures 6-7 to assets/data/search-results-by-task.json.

The page calls the two campaigns Agentic search (campaign L3PG) and CEM search (campaign A0).

Reads the same campaign reports as DexVerse/docs/figs/l3pg_dexverse_adroit/make_baseline_figures.py
(heldout_success_main.png, total_rollouts_main.png) and copies the L3PG held-out success videos
from DexVerse/docs/videos/l3pg_heldout_success unchanged. The gallery (Figure 7) lists every task; the
summary rows behind the Adroit/category charts leave out Adroit Pen and DexVerse Long-horizon (Section 4). Needs the source checkouts; run with the CaP-X venv, which has matplotlib:

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
# Renders made for the blog where the folder above has none, all on held-out seed 9000. With no accepted
# Agentic policy, a card shows CEM's accepted policy if a replay of it succeeds, otherwise a failed episode
# of the last submitted Agentic policy. None for RotateKnob (replays diverge from the saved evaluation at
# step 24 and time out) or CookFoods (CEM replays of seeds 9000, 9002 and 9010 all time out; 55 of its 84
# logged held-out successes end after 10 actions). task -> (file, outcome, arm)
EXTRA = Path("/home/djengof/DexVerse/Schema-Robo-dexverse/experiment_results/videos/blog_gallery_extra")
EXTRA_VIDEOS = {"OpenHuaweiPhone": ("OpenHuaweiPhone.mp4", "failure", "model_driven"),
                "OpenGlasses": ("OpenGlasses.mp4", "failure", "model_driven"),
                "LongHorizon-OvenBakeSalmon": ("OvenBakeSalmon.mp4", "failure", "model_driven")}
# The six E1 tasks (pooled 10 training positions) come from their own campaigns, e1_pool10_L3PG and
# e1_pool10_A0; they join the gallery but not the summary rows behind Figure 6.
E1_TASKS = ["BimanualLiftTray", "FunctionalHammerStrike", "GraspBucketPickUpCan",
            "LongHorizon-MicrowaveRetrievePlace", "OpenDrawer", "RelocateSphere"]
EXTRA_VIDEOS.update({t: (f"{t}.mp4", "success", "model_driven") for t in E1_TASKS})
sys.path.insert(0, str(FIGS))
from make_baseline_figures import A0_ADROIT, A0_DEX, BASELINE, load_e1  # noqa: E402
import make_figures  # noqa: E402
from make_figures import CATEGORIES, DEX_REPORT, HOME, by_category, load_adroit, load_dexverse, rate  # noqa: E402

SKIP = {"Pen", "Long-horizon"}  # left out of the summary charts only
# make_figures picks the newest finished Adroit run per task; the page reports the first runs (Hammer and
# Relocate have later r2 runs), so pin them here to keep the published Adroit numbers stable.
make_figures.ADROIT_RUNS = [(task, runs[-1:]) for task, runs in make_figures.ADROIT_RUNS]


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
                     resets=state["reset_count"], heldout=chain["heldout_repeats"] if chain["accepted"] else None, n=50,
                     evals=0, requests=0)  # by_category averages these too; nothing here reads them
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
    e1 = load_e1("L3PG")
    a0.update({r["task"]: r for r in load_e1("A0")})
    assert sorted(r["task"] for r in e1) == sorted(E1_TASKS)
    (ROOT / "assets/videos/model-driven").mkdir(parents=True, exist_ok=True)
    tasks = []
    order = {g: i for i, g in enumerate(["Adroit"] + CATEGORIES)}
    for r in sorted(adroit + dex + e1, key=lambda r: order[r["group"]]):  # stable: E1 tasks end each group
        group = r["group"]
        bench = "Adroit" if group == "Adroit" else "DexVerse"
        src, outcome, video_arm = VIDEOS / f"{bench}-{r['task']}.mp4", "success", "model_driven"
        if r["task"] in EXTRA_VIDEOS:
            name, outcome, video_arm = EXTRA_VIDEOS[r["task"]]
            src = EXTRA / name
        video = None
        if src.exists():
            video = f"assets/videos/model-driven/{bench}-{r['task']}.mp4"
            shutil.copy2(src, ROOT / video)
        tasks.append(dict(benchmark=bench, group=group, task=r["task"], video=video,
                          video_outcome=outcome if video else None, video_arm=video_arm if video else None,
                          heldout_repeats=r["heldout"], episodes=r["n"],
                          model_driven=arm(r), cem=arm(a0[r["task"]]), baseline=None))
    groups = [dict(group="Adroit", task=t["task"], model_driven=summary(next(r for r in adroit if r["task"] == t["task"])),
                   cem=summary(a0[t["task"]]), baseline=None) for t in tasks if t["benchmark"] == "Adroit" and t["task"] not in SKIP]
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
        "arms": {"model_driven": "Agentic search", "cem": "CEM search", "baseline": "Baseline (policy search), not yet run"},
        "heldout_metric": "Adroit: frozen policy on 30 unseen starts, one run. DexVerse: 50 unseen starts, mean of two "
                          "repeats. Unaccepted tasks count as 0%.",
        "rollouts_metric": "Total rollouts = parameter-search rollouts + policy-design resets.",
        "video_note": "One held-out episode per task, from Agentic search (video_arm: model_driven) unless noted: a success, or where Agentic search has no accepted policy, CEM search's accepted policy (video_arm: cem) or else a failed episode of the last submitted Agentic policy (video_outcome: failure); tasks with no recorded video show none.",
        "baseline_note": "Baseline values are null until the runs exist; " + ("all BASELINE entries are None"
                         if all(v["rollouts"] is None and v["rate"] is None for v in BASELINE.values()) else "see source"),
        "summary": groups,
        "tasks": tasks,
    }
    (ROOT / "assets/data/search-results-by-task.json").write_text(json.dumps(data, indent=1) + "\n")
    print(len(tasks), "tasks,", sum(t["video"] is not None for t in tasks), "videos")


if __name__ == "__main__":
    main()
