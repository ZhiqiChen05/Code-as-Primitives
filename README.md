# Code as Primitives

Project page for **Code as Primitives: Harnessing Frontier Models to Synthesize Low-Level Robotic Skills**.

Live site: <https://zhiqichen05.github.io/Code-as-Primitives/>

The page follows the active text and original figures in `../ExtendedAbstract/main.tex`, with additional Adroit experiments, the recorded Pen walkthrough, and the original detailed campaign results. The manuscript directory and experiment checkouts remain read only.

The title, author order, affiliations, contribution marks, social metadata and BibTeX use the manuscript's metadata: Zhiqi Chen, Djengo Cyun-Jyun Fang, Guanning Zeng, Xiuyu Li, Haiwen Feng and Andrea Zanette; Impossible Research and Carnegie Mellon University. Zhiqi Chen and Fang contributed equally, Zhiqi Chen is project lead, and Feng and Zanette are joint advisers.

## Preview and edit

This is a buildless static site. From the repository root:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Open <http://127.0.0.1:8000/>. Edit `index.html` for article content, `assets/styles.css` for layout, and `assets/site.js` for video previews and reading progress. Reduced-motion preferences disable automatic previews.

The hero uses the manuscript's overview figure. Section 2 explains controller synthesis and simulation-guided refinement. Figure 3 (`assets/loop.js`, `assets/loop.css`) preserves the eight-step interactive sequence: three mechanism steps and five recorded Pen artifacts. Its final panel also shows the four original Pen images extracted from the paper figure.

On larger desktop viewports, scrolling drives the sticky figure; Back/Next also select steps. With focus on those controls, Left/Right move one step and Home/End select the first/last step. At widths up to 1,240 px or heights below 740 px, manual navigation replaces the scroll layout. Without JavaScript, and in print, the artifacts remain visible alongside the static SVG and step descriptions.

## Results and figures

| Figure | Content | Data or source |
|---|---|---|
| 1 | Paper overview in the hero | `assets/figures/paper-overview.png`, with the original PDF available |
| 2 | Controller synthesis and parameter search | Inline diagram and the recorded stage-one Pen controller |
| 3 | Interactive learning loop and Pen evidence | `docs/pen-case-study.json`; existing scroll and Back/Next behavior |
| 4 | Paper DexVerse comparison: 15 baseline tasks and the remaining 60 | `assets/figures/paper-heldout-pair.png`, `assets/data/paper-dexverse-results.json` |
| 5 | Adroit random-reset held-out results | `assets/data/adroit-results.json`, `assets/data/adroit-protocol.json` |
| 6 | Earlier fixed-start versus random-reset Adroit campaigns | `assets/data/adroit-curriculum.json` |
| 7–8 | Original Opus held-out success and rollout costs | `assets/data/search-results-by-task.json` |
| 9 | Original 3-Adroit + 66-DexVerse task gallery | Same task data; `assets/evidence.js` and `assets/videos/model-driven/` |

The paper reports Agentic/CEM success of 95.9%/96.7% on 15 tasks, compared with a 46.0% mean of the best imitation-learning result on each task. On the remaining 60 tasks the means are 90.7%/94.0%. The earlier 75-task `L3+papers` campaign (94.3%, versus CEM 94.5%) remains a separate expandable result. The original gallery retains its grasp-aware `L3PG` cohort: 66 DexVerse tasks at 94.4%, versus CEM 96.0%, plus three Opus Adroit tasks. Its 97.3% figure applies only to the 64 accepted DexVerse policies. The independent Astra random-reset Adroit result is 119/120, or 99.2%.

These cohorts and protocols are deliberately named separately. Published imitation results provide comparisons under their reported settings; the page does not claim a matched rerun or a universal best result across every task or prior method. See [source notes](docs/source-notes.md) for the full campaign mapping and evidence boundaries.

## Evidence and asset generation

Paper-asset source paths, dimensions and SHA-256 hashes are in [paper-assets.json](assets/figures/paper-assets.json). The overview PDF and held-out PNG are copied unchanged; the overview PNG is rasterized from the PDF, and the four Pen JPEGs are extracted without cropping or recompression. To regenerate them with PyMuPDF and Pillow installed:

```sh
python3 scripts/prepare_paper_figures.py --source-dir ../ExtendedAbstract
```

Regenerate the other SVG figures using the Python standard library:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/generate_figures.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/generate_result_figures.py
```

The retained gallery export, `scripts/export_search_tasks.py`, needs the original DexVerse and Adroit checkouts and the paths documented in that script. It reads the original campaign reports and copies held-out success videos from `DexVerse/docs/videos/l3pg_heldout_success`; the checked-in data and media allow the site to run without those checkouts. Its original invocation was:

```sh
/home/djengof/CaP-X/cap-x/.venv/bin/python -I scripts/export_search_tasks.py
```

Media provenance is in `docs/adroit-media.json`, `docs/pen-case-study.json` and `docs/dexverse-media.json`; original chart provenance remains in `docs/figure-sources.json`. The optional `scripts/render_adroit_media.py` and `scripts/render_pen_case_study.py` reproduce Adroit videos from the local trajectories and require the dependencies documented in those scripts. Generated outputs and temporary data stay within this repository.

## Deployment

GitHub Pages publishes `main` at `/(root)`. `.nojekyll` serves these files directly. Use the authorized `page` tmux session for GitHub pushes in this workspace. `origin` points to `https://github.com/ZhiqiChen05/Code-as-Primitives.git`; `template` retains the original site source.

The initial template was [Schema Harness](https://schema-harness.github.io/), source commit `537a5f245408b91bc98b3cb77ec42b4633e96dd6`. Its content remains in Git history; the current article follows the Code as Primitives manuscript and experiment records.

DexVerse comparison videos and the copied archive report figure retain their MIT attribution in [DEXVERSE-LICENSE.txt](docs/DEXVERSE-LICENSE.txt). No new license is assigned to the original Schema template.
