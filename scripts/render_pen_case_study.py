#!/usr/bin/env python3
"""Export two historical Pen replays and an auditable case-study manifest.

Use the same simulator environment / offscreen-library settings documented in
render_adroit_media.py. Source repositories are read-only. No policy is executed
or optimized: only saved actions are replayed, then reconciled with saved states.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

from render_adroit_media import ROOT, digest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--historical-source", required=True, type=Path)
    args = parser.parse_args()
    source, historical = args.source.resolve(), args.historical_source.resolve()
    sys.path.insert(0, str(source))
    from env.adroit import AdroitEnv
    import imageio_ffmpeg
    import numpy as np
    from PIL import Image

    current = source / "experiment_results/adroit_seq10_l3pr/runs/pen_po_seq10_L3PR/runs/repetition_001/case-01/attempt_01"
    prior = historical / "experiment_results/pen_search_verified"
    old_report = json.loads((prior / "frozen_summary.json").read_text())
    old_episode = next(row for row in old_report["results"] if row["seed"] == 8300)
    neutral = current / "learning/episode_0000"
    jobs = [
        {"name": "adroit-pen-earlier", "source": prior / "frozen-8300/trajectory.jsonl", "seed": 8300, "success": True, "poster_step": 35, "label": "Earlier fixed-start search prototype · training-seed replay · 0.25× speed", "provenance": "No foundation-model author attribution is recorded for this prototype."},
        {"name": "adroit-pen-neutral", "source": neutral / "history.jsonl", "seed": json.loads((neutral / "run_state.json").read_text())["seed"], "success": False, "poster_step": 100, "label": "Astra stage 1 · neutral-grasp learning probe · 0.25× speed", "provenance": "Initial learning probe from the GPT-6 Astra / max-reasoning random-reset campaign; not held-out evaluation."},
    ]
    media = []
    for job in jobs:
        rows = [json.loads(line) for line in job["source"].read_text().splitlines() if line]
        env = AdroitEnv(task_variant="pen", seed=job["seed"], horizon=200, render_size=640)
        env.raw.mujoco_renderer.width, env.raw.mujoco_renderer.height = 640, 480
        frames, max_error = [], 0.0
        assert np.array_equal(env.observation.state.values, rows[0]["before"]["state"]["values"])
        try:
            for row in rows:
                obs, _ = env.step(row["action"])
                error = float(np.max(np.abs(np.asarray(obs.state.values) - row["after"]["state"]["values"])))
                max_error = max(max_error, error)
                assert error == 0.0, (job["name"], obs.step, error)
                assert obs.metrics.to_dict() == row["after"]["metrics"]
                frames.append(env.render())
            assert obs.success == job["success"]
            final_metrics = obs.metrics.to_dict()
        finally:
            env.close()
        video = ROOT / "assets/videos" / (job["name"] + ".mp4")
        temporary = ROOT / ".git/tmp" / video.name
        cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s:v", "640x480", "-r", "25", "-i", "pipe:0", "-an", "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(temporary)]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for frame in frames:
            p.stdin.write(frame.tobytes())
        p.stdin.close()
        assert p.wait() == 0
        temporary.replace(video)
        poster = ROOT / "assets/images" / (job["name"] + "-poster.jpg")
        Image.fromarray(frames[job["poster_step"] - 1]).save(poster, quality=92, optimize=True)
        media.append({"video": str(video.relative_to(ROOT)), "poster": str(poster.relative_to(ROOT)), "label": job["label"], "attribution": job["provenance"], "source_trajectory": str(job["source"]), "source_sha256": digest(job["source"]), "seed": job["seed"], "steps": len(rows), "native_control_hz": 100, "playback_fps": 25, "playback_speed": 0.25, "duration_seconds": len(rows) / 25, "replay_max_absolute_state_error": max_error, "replay_states_bitwise_equal": True, "replay_metrics_equal_every_step": True, "final_metrics": final_metrics, "video_sha256": digest(video)})
        print(job["name"], "verified", len(rows), "states", flush=True)

    search = {}
    for number in (1, 2, 4, 27, 30, 39, 44):
        path = current / f"search/search_{number:04}/result.json"
        result = json.loads(path.read_text())
        search[f"search_{number:04}"] = {"rollouts": result["rollouts"], "successes": sum(bool(c["official_episode_success"]) for c in result["candidates"]), "source": str(path), "sha256": digest(path)}
    submissions = json.loads((current / "submissions.json").read_text())
    heldout_path = source / "experiment_results/adroit_seq10_l3pr/heldout/pen_po_seq10_L3PR/evaluation.json"
    heldout = json.loads(heldout_path.read_text())
    first_heldout = heldout["episodes"][0]
    first_rows = [json.loads(line) for line in Path(first_heldout["trajectory_path"]).read_text().splitlines() if line]
    final_success_run = 0
    for row in reversed(first_rows):
        if not row["after"]["metrics"]["current_success"]:
            break
        final_success_run += 1
    current_clip_diagnostics = {
        "seed": first_heldout["seed"],
        "success_steps": first_heldout["final_metrics"]["success_steps"],
        "final_success_run": final_success_run,
        "final_current_success": first_heldout["final_metrics"]["current_success"],
        "minimum_recorded_pen_height_m": min(row["after"]["state"]["values"][26] for row in first_rows),
        "all_30_heldout_final_frames_successful": all(e["final_metrics"]["current_success"] for e in heldout["episodes"]),
    }
    case_study = {
        "model": "GPT-6 Astra", "model_id": "gpt-6-astra", "reasoning": "max", "campaign": "adroit_seq10_l3pr",
        "attribution_caveat": "The requested Opus step-by-step trace is unavailable in the supplied repository. This case study instead describes verifiable Astra tool actions, authored policies, saved notes and simulator outcomes. Opus aggregate results are separate and must not be substituted for this history.",
        "task": "Adroit Pen: 45 public observation values; 24 normalized actuator targets; 200 steps at native 100 Hz. Episode success requires more than 20 frames with position error <0.075 m and orientation dot product >0.95.",
        "source_events": str(current / "events.jsonl"), "source_events_sha256": digest(current / "events.jsonl"),
        "source_code_excerpts": {
            "orientation_gates": "phase = max(0.0, min(1.0, (0.75 - v[33]) * 6))\nthird = max(0.0, min(1.0, (0.5 - v[33]) * 5))",
            "target_selection": "t = v[36:39]\nbest = max(LIB, key=lambda r: sum((r[0][i] * t[i] for i in range(3))))",
            "source": "search/search_0039/result.json: best_source",
        },
        "iterations": [
            {"number": 1, "title": "Probe a neutral grasp", "description": "Write normalized actuator targets, execute 30 steps and then the remaining 170 steps, and inspect the pen's equilibrium. The recorded initial policy produces zero actuator commands and never meets the target success condition.", "event_lines": [44, 47, 86], "evidence": "learning/episode_0000/history.jsonl", "media": "assets/videos/adroit-pen-neutral.mp4"},
            {"number": 2, "title": "Search finger and wrist structure", "description": "Try grouped finger targets, independent-finger grasps and orientation-feedback controllers. Saved notes report that thumb-only rotation ejects the pen, while a flexed wrist helps retain a raised grasp. Candidate search provides measurements for these structural choices.", "event_lines": [293, 313, 374, 439, 1234, 1674], "evidence": ["search/search_0002/result.json", "search/search_0004/result.json", "search/search_0027/result.json"]},
            {"number": 3, "title": "Gate transitions on observed orientation", "description": "Combine a raised BASE grasp and a more vertical VERT grasp using the current pen axis, with phase = clip((0.75 - axis_x) * 6). Add another orientation gate to reach targets beyond vertical. These transitions use observed state rather than a playback clock.", "event_lines": [1271, 1323, 1524, 1674, 1777], "evidence": ["search/search_0027/result.json", "search/search_0030/result.json"]},
            {"number": 4, "title": "Select by target, then challenge the frozen policy", "description": "Select a grasp by alignment between its measured endpoint and the target axis. The first library succeeds on 10/16 fresh adaptive-search starts, then fails its first frozen submission. Reverse-tilt and position-compensation revisions expand the library: 21/32 adaptive-search starts succeed and the second frozen stage-1 submission passes.", "event_lines": [1698, 1701, 1777, 1780, 1802, 1827, 1857, 1895, 1905], "evidence": ["search/search_0039/result.json", "search/search_0044/result.json", "submissions.json"]},
        ],
        "search_batches": search,
        "stage1_submissions": [{"success": row["success"], "seed": row["case_results"][0]["seed"], "success_steps": row["case_results"][0]["final_metrics"]["success_steps"]} for row in submissions],
        "final_outcome": {"description": "After further refinement through stage 10, the final frozen Pen policy passes 30/30 separately reserved held-out starts. This is not the stage-1 library's held-out score.", "successes": sum(e["success"] for e in heldout["episodes"]), "episodes": len(heldout["episodes"]), "source": str(heldout_path), "source_sha256": digest(heldout_path), "media": "assets/videos/adroit-pen.mp4"},
        "current_clip_diagnostics": current_clip_diagnostics,
        "earlier_prototype": {"description": "An earlier fixed-start black-box search prototype blends two hard-coded 24-action vectors using the observed pen-axis z component. It passes the official aggregate criterion on training seed 8300, but drops the pen at step 69. Foundation-model authorship is not recorded.", "source": str(prior), "training_seed": 8300, "training_success_steps": 35, "first_drop_step": 69, "final_success_frame": False, "heldout_successes": sum(e["success"] for e in old_report["results"] if e["seed"] != 8300), "heldout_episodes": len(old_report["heldout_seeds"]), "media": "assets/videos/adroit-pen-earlier.mp4", "caveat": "Different training protocols, seeds and evaluation sample sizes; descriptive illustration, not a controlled ablation or causal improvement estimate."},
        "media": media,
    }
    (ROOT / "docs/pen-case-study.json").write_text(json.dumps(case_study, indent=2) + "\n")


if __name__ == "__main__":
    main()
