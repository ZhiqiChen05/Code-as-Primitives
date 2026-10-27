# Code as Primitives: evidence and media sources

The page's title, author metadata, central method and DexVerse headline results follow the active text of the fixed `ExtendedAbstract/main.tex` and its original figures. Commented-out manuscript prose is not treated as an active claim. Additional Adroit experiments, the Pen development walkthrough, search costs and long-horizon examples retain the evidence assembled from the author's 25 October 2026 outline and the experiment archives.

## Manuscript metadata and scope

The full title is **Code as Primitives: Harnessing Frontier Models to Synthesize Low-Level Robotic Skills**. The author order is Zhiqi Chen, Djengo Cyun-Jyun Fang, Guanning Zeng, Xiuyu Li, Haiwen Feng and Andrea Zanette. Affiliations and marks follow `main.tex`: Impossible Research and Carnegie Mellon University; equal contribution for Zhiqi Chen and Fang, project lead for Zhiqi Chen, and joint advising for Feng and Zanette. Page metadata and BibTeX use that title and order.

The method separates controller-class design from parameter optimization. A model writes a state-to-action program and can revise its structure or search its parameters using simulation feedback. Agentic search and CEM describe supported refinement modes; accepted programs execute without model calls. The page does not equate an optional parameter-search call with the complete learning process.

## DexVerse results and campaign mapping

Primary paper sources: `ExtendedAbstract/main.tex` and `ExtendedAbstract/figs/heldout_pair.png`. Numeric transcription, archive crosschecks, task lists and hashes are in `assets/data/paper-dexverse-results.json`.

- The paper evaluates 75 tasks across six categories, including four long-horizon tasks, using state observations without expert demonstrations. Frozen accepted policies are evaluated on 50 unseen initial and target configurations, repeated twice. The archived protocol reuses those same 50 configurations in both repeats; this is neither 100 distinct starts nor two independent training runs.
- On 15 tasks with published imitation baselines, Agentic and CEM search achieve 95.9% and 96.7%; the per-task best imitation result averages 46.0%. On the other 60 tasks, Agentic and CEM reach 90.7% and 94.0%. Figure 4 panel (b) covers those remaining 60 tasks, whose category counts sum to 60, rather than an additional 75-task evaluation.
- The CEM values cross-check against valid A0 rows from `e1_pool10_A0`, `e2_wave1_A0` and `e2_wave2_A0`, yielding an exact full-cohort mean of 94.52%. The 13 paper-comparison tasks shared with `results/opus-5.5/summary/L3PG.json` match its Agentic values exactly.
- The supplied L3PG archive covers 69 tasks and lacks the six E1 tasks. The fixed paper supplies the added comparison values for BimanualLiftTray (92%) and FunctionalHammerStrike (100%) and complete category aggregates. A full paper-Agentic campaign identity or all six added raw chains cannot be verified from the supplied archive. The new JSON therefore keeps paper-reported data separate from archive crosschecks instead of substituting the earlier L3P campaign or inventing per-repeat counts.
- The earlier `L3+papers` campaign remains available as a separate 75-task result: 73/75 accepted and 94.32% mean success, versus A0's 73/75 and 94.52%. Its six-category success and parameter-search table uses `assets/data/dexverse-results.json`. Unaccepted tasks count as zero.
- The earlier three-arm E2 comparison remains in `assets/data/dexverse-comparison-e2.json` and `assets/figures/dexverse-comparison-e2.svg`: on 69 tasks, A0 is 94.4%, L3+papers 94.1% and L3PG 91.6%. These are the archived E2 results, not the paper's remaining-60 split.
- The original detailed gallery is preserved in `assets/data/search-results-by-task.json`: 66 DexVerse tasks from that L3PG E2 cohort after excluding its three long-horizon tasks, plus three separate Opus Adroit tasks. On the 66 DexVerse tasks, the means are 94.3788% for L3PG and 96.0303% for A0, displayed as 94.4% and 96.0%. The 97.3% value is the accepted-only mean over 64 L3PG policies (97.328125%); OpenHuaweiPhone and OpenGlasses are the two unaccepted tasks. The earlier “70 tasks” label does not describe this denominator.
- `L3PG` adds task-general grasp-aware controller guidance to the Agentic search tools. The page uses “Agentic search” with the campaign identified in context; existing internal `model_driven` keys and media filenames are retained. `L3+papers`, `L3PG` and the Astra random-reset campaign must not be silently merged.
- The 75 valid tasks are filtered from the 100 registered DexVerse tasks in the source checkout. These are simulator-state results, not vision-only or real-robot results. Long-horizon composition and costs remain in `docs/dexverse-long-horizon.json`; a successful single-seed replay alone does not establish accepted-policy status.

The experiment checkout is `dexverse-llm-policy-search`, particularly `docs/method.md`, `results/opus-5.5/summary/{A0,L3P,L3PG}.json` and the comparison reports. The [public Opus run archive](https://huggingface.co/datasets/b09501048/dexverse-opus-5.5-runs) lists the earlier seven campaigns; its directory listing was checked on 27 October 2026.

### Imitation comparison

The 46.0% baseline is the average of 15 **per-task maxima** across π0.5, OpenVLA, DP3 and DP, not the mean of one fixed policy. Values match Table 3 of the [DexVerse paper](https://arxiv.org/html/2607.08751). Section 4.1 states that the four methods use the same 950 teleoperation episodes: 19 tasks with 50 episodes each.

Observation interfaces differ by method. Appendix B specifies RGB and language for π0.5 with proprioceptive input disabled; RGB, joint positions and language for OpenVLA; normalized proprioceptive state without vision for DP; and point clouds with proprioception for DP3. The local `scripts/compare_dexverse_table3.py` transcribes the baseline numbers correctly but summarizes those modalities too broadly. The site's JSON cites the primary paper and records the method-specific interfaces. Shared task names do not make these training resources or observations a matched ablation.

### Cost definitions

The earlier 75-task A0/L3+papers results support **mean parameter-search rollouts per task below 150 in four of six categories in each arm**. Those counts exclude learning episodes, training evaluations, held-out tests and uncounted interrupted work; they are not a claim of total interaction below 150.

Figures 7–9 use the original gallery's different metric: parameter-search rollouts plus policy-design resets. Training validation and held-out evaluations are excluded. The optional “Baseline (policy search)” remains unrun and has null values; it is distinct from the published imitation-learning results.

## Adroit

Source checkout: `Schema-Robo-v7-r1`. The result data remain in `assets/data/adroit-results.json` and `assets/data/adroit-curriculum.json`; the expanded `assets/data/adroit-protocol.json` records the full protocol, per-task seed lists, policy hashes, costs, stage submissions, source references and literature context.

- `docs/figures/adroit_seq10_l3pr/REPORT.md` and its CSV/JSON data support 119/120 held-out successes (99.2%): Door 29/30 and Hammer, Pen and Relocate 30/30 each. There is one training chain per task and 30 test seeds disjoint from adaptation seeds.
- The four archived `experiment_results/adroit_seq10_l3pr/runs/*/resolved_config.json` files identify GPT-6 Astra (`gpt-6-astra`, max reasoning). Fresh native reset seeds are used in learning, independent search rollouts and training validation. At stage k, one frozen submission must succeed on all k fresh episodes; all four tasks passed ten stages.
- Held-out execution uses 200 native actions per episode at 100 Hz, with no model calls or adaptation. Episode success counts native successful frames: more than 25 for Door, Hammer and Relocate, more than 20 for Pen. These are simulator-native success criteria, not a claim of arbitrary disturbance or real-world robustness.
- Ten stages do not mean ten simulator episodes. Pen used 6,095 search rollouts and 1,233,120 adaptation steps; Door used 8,858 search rollouts. The original campaign predates the later incoming-transfer shortcut.
- `docs/research.md` and `docs/data/astra_vs_opus.json` support the earlier fixed-start comparison (58/120, 48.3%). Its comparison with random-reset L3PR is descriptive: guidance, reset/test seeds and actual interaction effort differ. No independent held-out learning curves exist for stages 1–9, and the final 30/30 Pen result is not attributed to the stage-one controller.
- The original Opus gallery results on Door, Hammer and Relocate are a separate fixed-start Agentic/CEM campaign, not the 99.2% Astra experiment.

The Adroit literature comparison reports the published GPI and DP four-task means and the narrower DP3 three-task context, with links and protocol differences in `adroit-protocol.json`. It does not establish a matched rerun, a best result on every task, or a universal record across prior work. GPI and its DP row reach 100% on Door, compared with Astra's 29/30. Demonstration counts, observation interfaces and evaluation procedures remain attached to their own sources.

## Pen walkthrough

The interactive walkthrough uses the authentic GPT-6 Astra Pen record. The original outline named an Opus walkthrough, but matching raw Opus histories were unavailable in the supplied codebases and bounded historical search; no Opus progression is inferred.

`docs/pen-case-study.json` records exact events, source hashes and code excerpts. The 10/16 and 21/32 adaptive checks each repeat one parameter vector on fresh starts; they are neither counts of distinct successful controllers nor held-out evaluations. The controller-synthesis excerpt in Figure 2 and the expandable code in Figure 3 come from the saved stage-one policy in `search_0039`.

The earlier comparison uses the read-only historical `Schema-Robo-v6-c1/experiment_results/pen_search_verified` artifact. Its model attribution is unavailable. It passes the aggregate fixed-start criterion with 35 successful frames, drops at step 69 and passes 2/9 additional seeds. The newer policy uses a different protocol and 30 reserved seeds; the videos illustrate behavior rather than a matched ablation.

## Figure map and regeneration

The page originally drew layout and interaction inspiration from [Schema Harness](https://schema-harness.github.io/). Current numbering is:

| Figure | Asset and evidence |
|---|---|
| 1 | Hero overview: `assets/figures/paper-overview.png`, rasterized from the fixed manuscript's `figs/fig1_pen_v3-1.pdf`; original PDF linked. The pictured 30/30 concerns the Pen example. Letter writing is an illustration of skill composition, not another measured task. |
| 2 | Inline controller-synthesis and parameter-search diagram; recorded Pen controller excerpt. |
| 3 | Existing eight-step loop in `assets/loop.js` and `assets/loop.css`, combining three mechanism steps with five recorded Astra Pen artifacts. Scroll/Back/Next mechanics are preserved. Four original paper Pen images supplement the final held-out panel. |
| 4 | `assets/figures/paper-heldout-pair.png`: unchanged copy of the paper's Figure 2; 15 per-task baseline comparisons and six category means over the remaining 60 tasks. |
| 5 | `assets/figures/adroit-heldout.svg`: four-task random-reset Astra result and seed-level 95% Wilson intervals. |
| 6 | `assets/figures/adroit-curriculum.svg`: descriptive fixed-start versus random-reset campaign comparison. |
| 7 | `assets/figures/evidence-heldout.svg`: original Opus three-Adroit/66-DexVerse success comparison. |
| 8 | `assets/figures/evidence-rollouts.svg`: original Opus search-plus-reset accounting. |
| 9 | `assets/evidence.js` gallery: all 69 original task cards, with per-task results and available recorded replays. |

`assets/figures/paper-assets.json` records source and output SHA-256 hashes, dimensions, PDF image identifiers and extraction details. `scripts/prepare_paper_figures.py --source-dir ../ExtendedAbstract` requires PyMuPDF and Pillow. It copies the overview PDF and results PNG byte for byte, rasterizes the overview to 2400×1217, and extracts four original 300×224 JPEGs without cropping or recompression. The overview source PDF's SHA-256 is `921e64e5b2be8d011233430c5bacb2a8a72698584af31719aaaf39e7f5f9c5f1`; the copied results PNG is `7f6c59470456e90bce6b186813a8ebbc06f4cb5ab3858f7bc631e17fa8e00e24`. The rendered overview and extracted-image hashes are in the manifest.

`docs/figure-sources.json` retains the original SVG provenance. `scripts/generate_figures.py` generates the method overview and Adroit held-out chart with the Python standard library; `scripts/generate_result_figures.py` generates the DexVerse success/search-cost, Adroit curriculum and original detailed-comparison charts. Their numeric sources remain in `assets/data/`. The earlier 69-task three-arm SVG is redrawn from `results/opus-5.5/comparison_e2.md` using `assets/data/dexverse-comparison-e2.json`.

Figure 3's stages, tool names and acceptance boundaries follow the two harness codebases and DexVerse `docs/method.md`: L3+papers supplies model-designed candidates and numerical analysis, while A0 supplies host CEM. Training feedback may inform revision; held-out feedback may not. Desktop scrolling and Back/Next select the same sequence; smaller viewports use manual navigation. Without JavaScript and in print, the static overview, descriptions and artifact panels remain available.

## Media

- `docs/adroit-media.json`: four final held-out replays. All 800 saved state vectors and per-step metrics matched exactly. H.264, 640×480, 25 fps; native 100 Hz corresponds to 0.25× playback.
- `docs/pen-case-study.json`: the neutral probe and earlier prototype replay; all 400 saved state vectors and per-step metrics matched exactly. Both play at 0.25×.
- `docs/dexverse-media.json`: original side-by-side videos, URLs, hashes, sizes, seeds and visible outcomes. Originals were downloaded unchanged and decoded in full; posters are representative frames.
- The task gallery retains `assets/videos/model-driven/` and its per-task replay mapping, including the subsequently added failed final-policy episodes for OpenHuaweiPhone and OpenGlasses. Those two cards are marked FAILED, remain unaccepted, and retain zero-valued held-out scores. Burned-in campaign captions are cropped from view; internal filenames retain the archive naming. The MakeCoffee pair uses the public method labels.
- DexVerse archive videos and the copied archive report figure retain MIT attribution, copyright DjengoFang, from the [public Opus archive](https://huggingface.co/datasets/b09501048/dexverse-opus-5.5-runs). See `docs/DEXVERSE-LICENSE.txt`.

Assets and scripts are created or copied only into this blog repository. The paper and experiment repositories are read only; no new learning experiments or model calls were run. The page uses the supplied paper figures, verified source clips and data-derived charts rather than assuming that similarly named media from the original outline exist.
