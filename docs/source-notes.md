# Code as Primitives: draft evidence and media notes

The article follows the author-provided Notion outline, pasted into the conversation on 25 October 2026: motivation, early results, policy design plus parameter search, a Pen development walkthrough, held-out generalization, search costs, random-reset curriculum, and challenging Pen/long-horizon tasks.

## Sources and claim boundaries

### Adroit

Source checkout: `Schema-Robo-v7-r1`.

- `docs/figures/adroit_seq10_l3pr/REPORT.md` and its CSV/JSON data support the final random-reset results: 119/120 held-out episodes, one training chain per task, 30 disjoint test seeds per task.
- The four archived `experiment_results/adroit_seq10_l3pr/runs/*/resolved_config.json` files identify GPT-6 Astra (`gpt-6-astra`, max reasoning).
- `docs/research.md` and `docs/data/astra_vs_opus.json` supply the older fixed-start comparison. Comparing it with random-reset L3PR is descriptive, not a controlled causal curriculum experiment. Prompts, reset/test seeds, and actual interaction effort differ.
- Ten stages do not mean ten simulator episodes. Pen used 6,095 search rollouts and 1,233,120 adaptation steps; Door used more search rollouts.
- The original random-reset campaign did not include the incoming-transfer shortcut added to the harness later. The article describes the archived experiment.
- No independent held-out learning curves exist for stages 1–9 in this campaign. The final 30/30 Pen result is not attributed to the stage-one policy.

### Pen walkthrough

The requested outline named an Opus walkthrough. Raw Opus histories were unavailable in the supplied codebases and bounded historical search. The first draft therefore labels and uses the authentic GPT-6 Astra Pen record rather than inventing an Opus progression.

`pen-case-study.json` records the exact events, source hashes, and code excerpts. The 10/16 and 21/32 search checks each repeat one parameter vector on fresh starts. They measure adaptive rollout outcomes, not distinct successful candidate controllers or held-out generalization.

The earlier comparison comes from the read-only historical `Schema-Robo-v6-c1/experiment_results/pen_search_verified` artifact. Model attribution is unavailable. It passes the aggregate fixed-start criterion with 35 successful frames, drops at step 69, and passes 2/9 additional seeds. The newer policy uses another protocol and 30 reserved seeds; the video comparison is illustrative, not a matched ablation.

### DexVerse

Source checkout: `dexverse-llm-policy-search`, especially `docs/method.md` and `results/opus-5.5/summary/{A0,L3P,L3PG}.json`.

- Published Claude Opus 5.5 results: A0 and L3+papers each accept 73/75 valid tasks, with mean held-out success 94.5% and 94.3%, respectively. Unaccepted tasks count zero.
- The 75-task cohort is filtered from 100 registered tasks. Policies use simulator state; these are not vision-only or real-robot results.
- Two held-out repeats use the same 50 unseen starts; they are not 100 distinct starts or repeated independent training runs.
- L3PG is compared on the same 69-task E2 subset, not the 75-task cohort. Its mean is 91.6%, versus A0 94.4% and L3+papers 94.1% on that subset.
- The supported budget statement is **mean parameter-search rollouts per task below 150 in four of six categories**. Learning episodes, training evaluations, held-out tests, and uncounted interrupted work are excluded. No claim of total interaction below 150 is made.
- Long-horizon task composition and exact accounting are recorded in `dexverse-long-horizon.json`. Single-seed replay successes do not establish accepted-policy status.

The outline's claims about replacing control engineers or outperforming human demonstrations were treated as motivation rather than established empirical conclusions. No matched human-demonstration or real-world study is available here.

## Figures

Original project-page inspiration: [Schema Harness](https://schema-harness.github.io/).

- The interactive framework figure (Figure 3, `assets/loop.js`) adapts the mechanics of the Schema Harness Figure 3. Its stages, tool names and search/acceptance boundaries follow the two harness codebases and DexVerse `docs/method.md`: L3+papers uses model-designed candidate batches and numerical analysis; A0 supplies host CEM; training feedback can inform revision; held-out outcomes cannot. Its eight steps integrate three mechanism explanations and five GPT-6 Astra Pen artifacts from `docs/pen-case-study.json`, replacing the separate walkthrough. The synchronized panel includes the neutral-probe video, expandable policy excerpt, 10/16 and 21/32 adaptive checks, stage-one acceptance, and the final stage-ten held-out replay; no new results are shown. Figure 2's Level 1 excerpt and the expandable code come from the saved stage-one policy in `search_0039`. Desktop scrolling and Back/Next controls share one sequence; smaller viewports use manual navigation. Without JavaScript and in print, the static overview, step descriptions and all artifact panels remain available.
- `figure-sources.json` records source paths, hashes, captions, and limitations.
- `assets/data/` contains the numeric values behind the new SVG charts.
- `scripts/generate_figures.py` generates the method overview and Adroit held-out chart using the Python standard library.
- `scripts/generate_result_figures.py` generates the DexVerse held-out/search-cost and Adroit curriculum figures.
- The 69-task comparison chart (`assets/figures/dexverse-comparison-e2.svg`) is redrawn in the blog's figure style from the category table in the source repository's `results/opus-5.5/comparison_e2.md`; values are in `assets/data/dexverse-comparison-e2.json`.
- Method names: the blog calls the campaigns A0, L3+papers and L3PG (and the random-reset Adroit L3+papers run, L3PR) **CEM search**, **Agentic search** and **model-driven search**. Model-driven search is Agentic search plus a task-general prompt to design grasp-aware controllers. File and campaign paths keep the original identifiers. The Section 3 gallery videos carry a burned-in caption with the campaign name; the page crops that band out of view. The MakeCoffee pair in Section 4 was re-rendered with the public names.

## Media

- `adroit-media.json`: four final held-out replays. All 800 saved state vectors and per-step metrics matched exactly. H.264, 640×480, 25 fps; native 100 Hz means 0.25× playback speed.
- `pen-case-study.json`: the neutral learning probe and earlier prototype replay; all 400 saved state vectors and per-step metrics matched exactly. Both play at 0.25×.
- `dexverse-media.json`: original side-by-side videos, source URLs, exact hashes, sizes, seeds, and visible outcomes. Originals were downloaded unchanged and decoded in full; JPG posters are representative video frames.
- DexVerse videos and copied report figure are from the [public Opus archive](https://huggingface.co/datasets/b09501048/dexverse-opus-5.5-runs), MIT, copyright DjengoFang. See `DEXVERSE-LICENSE.txt`.

All assets and scripts were created or copied into the blog repository. The experiment codebases were read only; no new learning experiments or model calls were run. The filenames `dexverse_adroit_heldout_grid.mp4`, `heldout_success.png`, and `total_rollouts.png` mentioned in the outline were not present, so the draft uses verified source clips and regenerated figures.
