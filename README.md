# Code as Primitives

First project-blog draft: **Few-shot agentic policy learning for low-level robotic control**.

Live site: <https://zhiqichen05.github.io/Code-as-Primitives/>

## Preview and edit

This is a buildless static site. From the repository root:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Open <http://127.0.0.1:8000/>. Edit `index.html` for article content, `assets/styles.css` for layout, and `assets/site.js` for the video previews, keyboard-accessible tabs, and reading progress.

The opening uses text on the left and four Adroit videos on the right; the layout stacks on mobile. The page includes an interactive framework figure with recorded Pen artifacts, downloadable result data, search-budget and curriculum figures, and recorded manipulation comparisons. Reduced-motion preferences disable automatic previews.

Section 2 follows the "Thinking like a physicist" section of the Schema Harness template. Figure 2 shows policy design and parameter search. Figure 3 (`assets/loop.js`, `assets/loop.css`) combines the mechanism and its evidence in one eight-step sequence: three steps explain the outer loop, rollout ledger and inner search; five open the recorded Pen probe, policy design, search check, revision and final held-out replay. One artifact panel is active at a time, with native video controls and an expandable policy excerpt. There is no separate tabbed walkthrough.

On larger desktop viewports, scrolling drives the sticky figure; Back/Next also select steps. With focus on those controls, Left/Right move one step and Home/End select the first/last step. At widths up to 1,240 px or heights below 740 px, manual navigation replaces the scroll layout and keeps text and media at readable sizes. Without JavaScript, and in print, all five artifacts remain visible alongside the static SVG and step descriptions.

Section 3 follows the "What the numbers say" section of the Schema Harness template, in this site's own style: Figures 1, 4 and 5 compare held-out success and total rollouts for model-driven search, CEM search and a pending baseline (Adroit Pen and DexVerse Long-horizon are left to Section 4), and Figure 6 (`assets/evidence.js`) is a drag-scroll gallery of all 69 remaining tasks, each with its model-driven search held-out success replay and per-task bars. Its data, `assets/data/search-results-by-task.json`, and the videos in `assets/videos/model-driven/` (copied unchanged from `DexVerse/docs/videos/l3pg_heldout_success`) come from `scripts/export_search_tasks.py`, which needs the DexVerse and Adroit checkouts:

```sh
/home/djengof/CaP-X/cap-x/.venv/bin/python -I scripts/export_search_tasks.py
```

## Evidence and media

See [source notes](docs/source-notes.md) for result definitions, experiment boundaries, and adaptations from the author's outline. Media provenance and checksums are in `docs/adroit-media.json`, `docs/pen-case-study.json`, and `docs/dexverse-media.json`.

Regenerate the SVG figures without installing dependencies:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/generate_figures.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/generate_result_figures.py
```

The optional `scripts/render_adroit_media.py` and `scripts/render_pen_case_study.py` reproduce the Adroit videos from the original local trajectories. They require the source checkouts and simulation/media dependencies documented in the scripts. Their outputs and temporary data stay within this repository.

## Deployment

GitHub Pages publishes `main` at `/(root)`. `.nojekyll` serves these files directly. Use the authorized `page` tmux session for GitHub pushes in this workspace. `origin` points to `https://github.com/ZhiqiChen05/Code-as-Primitives.git`; `template` retains the original site source.

The initial template was [Schema Harness](https://schema-harness.github.io/), source commit `537a5f245408b91bc98b3cb77ec42b4633e96dd6`. Its content remains in Git history; the current article and layout are a new draft based on the author's project materials.

DexVerse comparison videos and the copied report figure retain their MIT attribution in [DEXVERSE-LICENSE.txt](docs/DEXVERSE-LICENSE.txt). No new license is assigned to the original Schema template.
