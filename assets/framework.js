/* Explanatory control-loop stepper. No experiment results are simulated. */
(() => {
  "use strict";
  const STEPS = [
    {title:"Choose a controller family.",phase:"DESIGN",nodes:["design"],edges:[],changes:"Features, feedback rules and program branches.",fixed:"Foundation-model weights; task and action interface.",label:"POLICY INTERFACE",description:"The model reads the task contract and authors a program that maps the current observation to actuator commands. Its structure is a hypothesis about how to control the task.",code:"def select_action(observation):\n    features = read_state(observation)\n    return controller(features, PARAMS)",note:"Illustrative pseudocode for the policy interface."},
    {title:"Expose the numerical choices.",phase:"PARAMETERIZE",nodes:["params"],edges:["design-params"],changes:"Literal parameter values and their declared bounds.",fixed:"The controller structure within a candidate batch.",label:"POLICY SOURCE",description:"A literal PARAMS vector exposes the authored constants: gains, thresholds or targets. Candidate evaluations can compare settings within the same controller family.",code:"policy.py\n  ├─ select_action(observation)\n  └─ PARAMS: literal numeric vector\n\nsearch bounds: lower < upper",note:"Search varies these constants while preserving the controller’s structure within a batch."},
    {title:"Run counted native trials.",phase:"OPTIONAL SEARCH",nodes:["params","trials"],edges:["params-trials"],changes:"Candidate parameter vectors, chosen within bounds.",fixed:"The submitted family during this batch; native task rules.",label:"SEARCH INTERFACE",description:"The model proposes candidate batches. Each candidate runs a policy in the native simulator; its actions and rollout count are charged. Numerical analysis itself has no simulator access.",code:"evaluate_candidates(candidate_vectors)\n    → native rollouts\n    → counted actions + outcomes\n\nrun_compute(analysis_code)\n    → NumPy / SciPy, no simulator",note:"In L3+papers, the model can design its search procedure and consult task reference texts. Search remains optional."},
    {title:"Read what the policy actually did.",phase:"TRAINING FEEDBACK",nodes:["evidence"],edges:["trials-evidence"],changes:"The agent’s evidence and assessment of the controller.",fixed:"Recorded outcomes; native success criterion.",label:"PUBLIC EVIDENCE",description:"Scores summarize a rollout; trajectories reveal how it unfolded. The agent can inspect task success, errors and observed transitions before deciding what to try next.",code:"public evidence\n  • observations + actions\n  • candidate scores\n  • native task success\n  • execution errors",note:"A high search score does not replace the task’s native acceptance rule."},
    {title:"Revise the hypothesis—or search again.",phase:"ADAPT",nodes:["evidence","design","params"],edges:["evidence-design"],changes:"The controller family, parameters, or next batch.",fixed:"Foundation-model weights; collected evidence.",label:"TWO WAYS TO REVISE",description:"Evidence can motivate a new feedback rule or a different branch. If the family remains useful, the agent can instead refine its numerical settings and request another batch.",code:"structure needs work?\n    revise policy.py\n\nfamily remains useful?\n    choose the next parameter batch",note:"The dashed return arrow belongs to training. No held-out outcome enters this loop."},
    {title:"Freeze one candidate for validation.",phase:"TRAINING SUBMISSION",nodes:["training"],edges:["evidence-training"],changes:"Which completed controller is submitted.",fixed:"Code and parameters throughout the submitted evaluation.",label:"IMMUTABLE SUBMISSION",description:"A submission freezes a controller and runs the training acceptance test. The author cannot edit code or intervene in individual actions while that evaluation executes.",code:"submit_to_eval()\n    → frozen policy snapshot\n    → native training-start episodes\n    → apply the acceptance rule",note:"A directly authored policy may reach this step without using parameter search."},
    {title:"Acceptance is a separate gate.",phase:"TRAINING ACCEPTANCE",nodes:["training","evidence"],edges:["training-evidence"],changes:"Further adaptation after a failed submission, within budget.",fixed:"One immutable policy across a submission’s episodes.",label:"ACCEPTANCE RULE",description:"In the recorded Adroit random-reset curriculum, stage k requires a single frozen submission to pass all k fresh starts. A failed submission can supply training evidence for another revision; successes do not accumulate across submissions.",code:"Adroit random-reset stage k\n    one policy × k fresh starts\n    all k must pass together\n\nfailure → training feedback\npass → next stage / finish training",note:"This shows the gate, not a fabricated pass or failure. Other protocols use their own exposed training-start sets."},
    {title:"Assess the frozen program on unseen starts.",phase:"HELD-OUT ASSESSMENT",nodes:["heldout"],edges:["training-heldout"],changes:"The held-out initial state and each observed control state.",fixed:"Selected policy, parameter values and checkpoint identity.",label:"NO MODEL IN THE CONTROL LOOP",description:"After training ends, the protocol-selected checkpoint runs on reserved held-out starts. Each observation drives the same frozen program. These outcomes measure generalization and are never returned to learning.",code:"observation\n    ↓\nfrozen select_action(observation)\n    ↓\nnative actuator targets\n\nNo model-provider calls or edits.",note:"Held-out testing also follows early training termination when a valid checkpoint exists. It cannot turn a failed training chain into an accepted one."}
  ];

  document.querySelectorAll("[data-framework-loop]").forEach((root, instance) => {
    const q = (selector) => root.querySelector(selector);
    const graph = q("[data-fx-graph]"), svg = q("[data-fx-edges]");
    const ui = q(".fx-ui"), nodes = [...root.querySelectorAll("[data-fx-node]")];
    if (!graph || !svg || !ui || nodes.length !== 6) return;
    let step = 0, mode = "l3", timer = null, playing = false, frame = null;
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
    const ns = "http://www.w3.org/2000/svg", markerId = `fx-arrow-${instance}`;
    const nodeMap = new Map(nodes.map((node) => [node.dataset.fxNode, node]));
    const make = (name, attrs) => {const el = document.createElementNS(ns, name);Object.entries(attrs).forEach(([key,value]) => el.setAttribute(key, value));return el;};
    const marker = make("marker", {id:markerId,viewBox:"0 0 8 8",refX:"7",refY:"4",markerWidth:"7",markerHeight:"7",orient:"auto",markerUnits:"userSpaceOnUse"});
    marker.append(make("path", {d:"M 0 0 L 8 4 L 0 8 Z",fill:"context-stroke"}));
    const defs = make("defs", {});defs.append(marker);svg.append(defs);
    const edgeSpecs = [["design-params","design","params"],["params-trials","params","trials"],["trials-evidence","trials","evidence"],["evidence-training","evidence","training"],["training-heldout","training","heldout"],["evidence-design","evidence","design"],["training-evidence","training","evidence"]];
    const paths = new Map();
    edgeSpecs.forEach(([id]) => {const el = make("path", {class:`fx-edge${id === "evidence-design" || id === "training-evidence" ? " fx-return" : ""}`,"marker-end":`url(#${markerId})`});paths.set(id,el);svg.append(el);});
    const labels = [make("text", {class:"fx-edge-label","text-anchor":"middle"}),make("text", {class:"fx-edge-label","text-anchor":"middle"})];
    labels[0].textContent="revise code / choose next batch";labels[1].textContent="failed training submission → feedback";labels.forEach(el=>svg.append(el));

    const layout = () => {
      frame = null;
      const bounds = graph.getBoundingClientRect();if (!bounds.width) return;
      svg.setAttribute("viewBox",`0 0 ${bounds.width} ${bounds.height}`);
      const boxes = new Map(nodes.map(node=>{const r=node.getBoundingClientRect();return [node.dataset.fxNode,{l:r.left-bounds.left,r:r.right-bounds.left,t:r.top-bounds.top,b:r.bottom-bounds.top,x:r.left-bounds.left+r.width/2,y:r.top-bounds.top+r.height/2}];}));
      const mobile = getComputedStyle(graph).gridTemplateColumns.split(" ").length === 1;
      edgeSpecs.forEach(([id,from,to])=>{
        const a=boxes.get(from), b=boxes.get(to);let d;
        if(id==="evidence-design") d=mobile?`M ${a.l} ${a.y} H 12 V ${b.y} H ${b.l-5}`:`M ${a.x} ${a.t-3} V ${a.t-38} H ${b.x} V ${b.b+5}`;
        else if(id==="training-evidence") d=mobile?`M ${a.r} ${a.y} H ${bounds.width-12} V ${b.y} H ${b.r+5}`:`M ${a.x} ${a.b+3} V ${Math.max(a.b,b.b)+30} H ${b.x} V ${b.b+5}`;
        else if(mobile || Math.abs(a.x-b.x)<5) d=`M ${a.x} ${a.b+3} V ${b.t-5}`;
        else if(b.x>a.x) d=`M ${a.r+3} ${a.y} H ${b.l-5}`;
        else d=`M ${a.l-3} ${a.y} H ${b.r+5}`;
        paths.get(id).setAttribute("d",d);
      });
      const a=boxes.get("evidence"), b=boxes.get("design"), t=boxes.get("training");
      labels[0].setAttribute("x",(a.x+b.x)/2);labels[0].setAttribute("y",a.t-44);
      labels[1].setAttribute("x",(a.x+t.x)/2);labels[1].setAttribute("y",Math.max(a.b,t.b)+45);
    };
    const scheduleLayout=()=>{if(frame===null)frame=requestAnimationFrame(layout);};
    const stop=()=>{if(timer!==null)clearTimeout(timer);timer=null;playing=false;root.dataset.playing="false";q("[data-fx-action=play]").setAttribute("aria-pressed","false");q("[data-fx-play-label]").textContent=step===STEPS.length-1?"Replay walkthrough":"Play walkthrough";q("[data-fx-play-icon]").textContent="▷";};
    const render=(announce=true)=>{
      const s=STEPS[step];
      nodes.forEach(node=>{const active=s.nodes.includes(node.dataset.fxNode);node.classList.toggle("is-active",active);node.setAttribute("aria-pressed",String(active));});
      paths.forEach((path,id)=>path.classList.toggle("is-active",s.edges.includes(id)));
      let description=s.description, code=s.code, note=s.note;
      if(mode==="a0"&&step===2){description="The host cross-entropy method (CEM) samples parameter vectors, executes native candidate episodes, and updates its distribution toward better candidates. The model can inspect the results and revise its controller family.";code="host CEM\n    sample parameter vectors\n    run counted native rollouts\n    refit toward better candidates\n\nmodel → inspect / revise policy";note="A0 supplies a built-in optimizer. It still requires frozen training acceptance; search can be skipped.";}
      if(mode==="a0"&&step===6){description="In the fixed-start sequential Adroit A0 experiments, stage k requires one frozen policy to pass the complete prefix of k training starts. Failed submissions can supply evidence for revision while budgets remain. Acceptance is separate from search ranking.";code="Adroit fixed-start stage k\n    one policy × k exposed starts\n    all k must pass together\n\nfailure → training feedback\npass → next stage / finish training";note="The training-start rule depends on the protocol. The A0 comparison used a growing fixed prefix; the featured L3PR campaign used fresh random validation starts.";}
      q("[data-fx-title]").textContent=s.title;q("[data-fx-phase]").textContent=s.phase;q("[data-fx-description]").textContent=description;q("[data-fx-changes]").textContent=s.changes;q("[data-fx-fixed]").textContent=s.fixed;q("[data-fx-code-label]").textContent=s.label;q("[data-fx-code]").textContent=code;q("[data-fx-code-note]").textContent=note;
      q("[data-fx-counter]").textContent=`${String(step+1).padStart(2,"0")} / ${String(STEPS.length).padStart(2,"0")}`;
      q(".fx-progress").setAttribute("aria-valuenow",String(step+1));q(".fx-progress").setAttribute("aria-valuetext",`Step ${step+1} of ${STEPS.length}: ${s.title}`);q("[data-fx-progress]").style.width=`${(step+1)/STEPS.length*100}%`;
      q("[data-fx-action=back]").setAttribute("aria-disabled",String(step===0));q("[data-fx-action=next]").setAttribute("aria-disabled",String(step===STEPS.length-1));q("[data-fx-action=reset]").setAttribute("aria-disabled",String(step===0&&!playing));
      if(!playing)q("[data-fx-play-label]").textContent=step===STEPS.length-1?"Replay walkthrough":"Play walkthrough";
      if(announce)q("[data-fx-announcement]").textContent=`${mode==="l3"?"L3 plus papers":"A0"}. Step ${step+1} of ${STEPS.length}. ${s.title} ${description}`;
      scheduleLayout();
    };
    const go=(next)=>{stop();step=Math.max(0,Math.min(STEPS.length-1,next));render();};
    const tick=()=>{timer=setTimeout(()=>{timer=null;if(!playing)return;if(step<STEPS.length-1){step+=1;render();}if(step===STEPS.length-1){stop();render(false);}else tick();},6500);};
    root.addEventListener("click",event=>{
      const button=event.target.closest("button");if(!button||!root.contains(button)||button.disabled||button.getAttribute("aria-disabled")==="true")return;
      if(button.dataset.fxMode){mode=button.dataset.fxMode;stop();root.querySelectorAll("[data-fx-mode]").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.fxMode===mode)));q("[data-fx-mode-note]").textContent=mode==="l3"?"The model chooses candidate batches and numerical analysis; the simulator executes each counted trial.":"The host runs CEM parameter search; the model can inspect evidence and revise the controller.";render();return;}
      if(button.dataset.fxJump!==undefined){go(Number(button.dataset.fxJump));return;}
      const action=button.dataset.fxAction;
      if(action==="next")go(step+1);else if(action==="back")go(step-1);else if(action==="reset")go(0);
      else if(action==="play") {if(playing){stop();render(false);}else{if(step===STEPS.length-1)step=0;playing=true;root.dataset.playing="true";button.setAttribute("aria-pressed","true");q("[data-fx-play-label]").textContent="Pause walkthrough";q("[data-fx-play-icon]").textContent="Ⅱ";render();tick();}}
    });
    root.addEventListener("keydown",event=>{if(!event.target.closest(".fx-controls")||event.altKey||event.ctrlKey||event.metaKey)return;if(event.key==="ArrowRight"){event.preventDefault();go(step+1);}else if(event.key==="ArrowLeft"){event.preventDefault();go(step-1);}else if(event.key==="Home"){event.preventDefault();go(0);}else if(event.key==="End"){event.preventDefault();go(STEPS.length-1);}});
    document.addEventListener("visibilitychange",()=>{if(document.hidden){stop();render(false);}});
    const motionChange=()=>{if(reduced.matches){stop();render(false);}};reduced.addEventListener?.("change",motionChange);
    if("ResizeObserver"in window)new ResizeObserver(scheduleLayout).observe(graph);else window.addEventListener("resize",scheduleLayout);
    if(document.fonts?.ready)document.fonts.ready.then(scheduleLayout);
    ui.hidden=false;root.classList.add("fx-ready");root.dataset.playing="false";render(false);
  });
})();
