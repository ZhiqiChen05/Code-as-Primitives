# Code as Primitives

First project-blog draft: **Few-shot agentic policy learning for low-level robotic control**.

Live site: <https://zhiqichen05.github.io/Code-as-Primitives/>

## Preview and edit

This is a buildless static site. From the repository root:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Open <http://127.0.0.1:8000/>. Edit `index.html` for article content, `assets/styles.css` for layout, and `assets/site.js` for the video previews, keyboard-accessible tabs, and reading progress.

The opening uses text on the left and four Adroit videos on the right; the layout stacks on mobile. The page includes a steppable framework, a four-step Pen walkthrough, downloadable result data, search-budget and curriculum figures, and recorded manipulation comparisons. Reduced-motion preferences disable automatic previews.

The interactive framework lives in `assets/framework.js` and `assets/framework.css`. Eight steps explain policy design, optional parameter search, training feedback, acceptance, and frozen held-out execution. Readers can click nodes, switch L3+papers/A0 search, or use Play, Back, Next, and Reset. Arrow keys, Home, and End work while a playback control has focus. Playback starts paused. Without JavaScript, and in print, the static SVG remains available.

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
