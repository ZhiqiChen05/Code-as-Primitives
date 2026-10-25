#!/usr/bin/env python3
"""Render verified saved Adroit actions; never run or train an authored policy.

Use a Python environment containing the source project's pinned simulator stack,
Pillow and imageio-ffmpeg. Run with PYTHONDONTWRITEBYTECODE=1 and point
MUJOCO_GL / LD_LIBRARY_PATH at an available offscreen renderer. This checkout's
generation used OSMesa extracted under .git/osmesa, with the system libstdc++
preloaded for compatibility with the existing Python environment.

Example (from the blog checkout):
  PYTHONDONTWRITEBYTECODE=1 MUJOCO_GL=osmesa \
  LD_LIBRARY_PATH="$PWD/.git/osmesa/usr/lib/x86_64-linux-gnu" \
  LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6 \
  PYTHONPATH="$PWD/.git/media-tools" /path/to/simulator/python -B \
  scripts/render_adroit_media.py --source /path/to/Schema-Robo-v7-r1

All output, cache and temporary paths are confined to this blog checkout.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
for variable, relative in {
    "TMPDIR": ".git/tmp",
    "XDG_CACHE_HOME": ".git/cache",
    "MPLCONFIGDIR": ".git/cache/matplotlib",
}.items():
    path = ROOT / relative
    path.mkdir(parents=True, exist_ok=True)
    os.environ[variable] = str(path)
os.environ.setdefault("MUJOCO_GL", "osmesa")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--campaign", default="adroit_seq10_l3pr")
    parser.add_argument("--fps", type=int, default=25)
    args = parser.parse_args()
    if args.fps <= 0:
        parser.error("fps must be positive")
    source = args.source.resolve()
    sys.path.insert(0, str(source))

    from env.adroit import AdroitEnv
    import imageio_ffmpeg
    import numpy as np
    from PIL import Image

    videos = ROOT / "assets/videos"
    images = ROOT / "assets/images"
    videos.mkdir(parents=True, exist_ok=True)
    images.mkdir(parents=True, exist_ok=True)
    records = []

    for task in ("door", "hammer", "pen", "relocate"):
        evaluation_path = source / "experiment_results" / args.campaign / "heldout" / f"{task}_po_seq10_L3PR" / "evaluation.json"
        evaluation = json.loads(evaluation_path.read_text())
        # Consistent first test episode, not a cherry-picked best trial.
        episode = evaluation["episodes"][0]
        trajectory_path = Path(episode["trajectory_path"])
        trajectory = [json.loads(line) for line in trajectory_path.read_text().splitlines()]
        native_hz = float(trajectory[0]["settle_info"]["control_hz"])
        for row in trajectory:
            assert float(row["settle_info"]["control_hz"]) == native_hz
        assert episode["provider_calls"] == 0
        env = AdroitEnv(task_variant=task, seed=episode["seed"], horizon=len(trajectory), render_size=640)
        # Change image framing only; preserve the simulator and its native camera.
        env.raw.mujoco_renderer.width = 640
        env.raw.mujoco_renderer.height = 480
        frames = []
        max_error = float(np.max(np.abs(np.asarray(env.observation.state.values) - trajectory[0]["before"]["state"]["values"])))
        exact = max_error == 0.0
        try:
            for row in trajectory:
                obs, _ = env.step(row["action"])
                actual = np.asarray(obs.state.values)
                expected = np.asarray(row["after"]["state"]["values"])
                error = float(np.max(np.abs(actual - expected)))
                max_error = max(max_error, error)
                exact = exact and bool(np.array_equal(actual, expected))
                if error > 1e-8:
                    raise RuntimeError(f"{task} replay diverged at step {obs.step}: {error}")
                if obs.metrics.to_dict() != row["after"]["metrics"]:
                    raise RuntimeError(f"{task} metrics differ at step {obs.step}")
                frames.append(env.render())
            assert obs.success == episode["success"]
            assert obs.done and len(frames) == episode["actions"]
            versions = env.evaluator_configuration()["versions"]
        finally:
            env.close()

        video_path = videos / f"adroit-{task}.mp4"
        temporary_video = ROOT / ".git/tmp" / video_path.name
        cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s:v", "640x480", "-r", str(args.fps), "-i", "pipe:0", "-an", "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(temporary_video)]
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        try:
            for frame in frames:
                process.stdin.write(frame.tobytes())
            process.stdin.close()
            if process.wait() != 0:
                raise RuntimeError(f"ffmpeg encoding failed for {task}")
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
        temporary_video.replace(video_path)
        poster_step = min(len(frames), max(80, int(episode["final_metrics"].get("first_success_step") or 100) + 15))
        poster_path = images / f"adroit-{task}-poster.jpg"
        Image.fromarray(frames[poster_step - 1]).save(poster_path, quality=92, optimize=True)
        record = {
            "task": task,
            "video": str(video_path.relative_to(ROOT)),
            "poster": str(poster_path.relative_to(ROOT)),
            "source_repository": str(source),
            "source_evaluation": str(evaluation_path.relative_to(source)),
            "source_evaluation_sha256": digest(evaluation_path),
            "source_trajectory": str(trajectory_path.relative_to(source)),
            "source_trajectory_sha256": digest(trajectory_path),
            "source_policy_hashes": episode["source_hashes"],
            "episode": episode["case_id"],
            "selection": "First planned held-out episode for every task, without ranking outcomes.",
            "seed": episode["seed"],
            "heldout_success": episode["success"],
            "provider_calls": 0,
            "steps": len(trajectory),
            "native_control_hz": native_hz,
            "playback_fps": args.fps,
            "playback_speed": args.fps / native_hz,
            "playback_caption": f"Verified held-out replay · {args.fps / native_hz:g}× speed",
            "duration_seconds": len(frames) / args.fps,
            "resolution": [640, 480],
            "poster_step": poster_step,
            "replay_max_absolute_state_error": max_error,
            "replay_states_bitwise_equal": exact,
            "replay_metrics_equal_every_step": True,
            "video_sha256": digest(video_path),
            "video_bytes": video_path.stat().st_size,
            "simulator_versions": versions,
            "note": "Video is a deterministic native-simulator rendering of recorded test actions, not a new learned policy or new independent test. All 200 states and metrics were reconciled before export. Camera/render dimensions do not alter physics.",
        }
        records.append(record)
        print(f"{task}: {len(frames)} frames, max state error {max_error:g}, {video_path.stat().st_size} bytes", flush=True)
        del frames

    destination = ROOT / "docs/adroit-media.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps({"campaign": args.campaign, "generation_script": "scripts/render_adroit_media.py", "clips": records}, indent=2) + "\n")


if __name__ == "__main__":
    main()
