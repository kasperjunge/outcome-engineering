# Diary: overview strategy and vision UI

This records the UI work to make top-level product context visible in the graph overview and restyle the local graph editor toward an Excalidraw-like canvas.

## Step 1: Render vision and strategy as overview nodes

**Author:** main

### Prompt Context

**Verbatim prompt:** UI, I want the vision and strategy to be visual in the overview view also so you can actually see them there as nodes,
**Interpretation:** The overview should not hide `VISION.md` and `STRATEGY.md` behind header buttons only; they should appear as graph nodes alongside ICPs and outcomes.
**Inferred intent:** Make strategic context visible at the same level as delivery context so the product graph reads from vision and strategy into ICPs and outcomes.

### What I did

I updated `/src/outcome_engineering/serve.py` so `build_graph_payload` includes `vision` and `strategy` in `nodes`, while marking root-file nodes as `deletable: false`. I updated `/src/outcome_engineering/templates/graph.html` to add vision and strategy bands above ICPs and outcomes, draw structural overview edges from vision to strategy and from strategy to outcomes, and hide the Delete button for non-deletable nodes. I updated `/tests/test_graph.py` to assert that `vision.product` and `strategy.product` are payload nodes and that root-file nodes are protected from deletion.

### Why

The previous API contract explicitly treated vision and strategy as prose context, which made the overview incomplete for strategic review. Rendering them as nodes makes the overview match the graph's conceptual hierarchy without changing filesystem structure.

### What worked

The existing discovery code already found root `VISION.md` and `STRATEGY.md`, so the backend change was small. The overview renderer could add bands without changing focus-mode behavior.

### What didn't work

The in-app browser tool failed during verification with `Mcp error: -32602: js: codex/sandbox-state-meta: missing field sandboxPolicy`. I switched to `playwright-cli` and verified against a local `oe serve` instance instead. Two initial `playwright-cli run-code` commands failed with `SyntaxError: missing ) after argument list` because the shell expanded `$$` in `page.$$eval`; I reran the checks with safer quoting and `playwright-cli eval`.

### What I learned

Top-level marker files reuse the graph root slug, so the generated ids are `vision.<root-name>` and `strategy.<root-name>`. The UI can treat them like nodes for editing and selection, but deletion still needs root-file protection.

### What was tricky

The schema still exposes root creation for strategies because strategy collection nodes are valid, while `VISION.md` is a singleton root file. The UI therefore needed to render both kinds as nodes without implying that all root-file nodes are deletable or creatable in the same way.

### What warrants review

Review `/src/outcome_engineering/serve.py` for the new payload contract and `/src/outcome_engineering/templates/graph.html` for overview band positioning and delete-button behavior. Validate with `uv run pytest`, `uv run oe validate product`, and a served overview graph.

### Future work

If multiple dated strategy nodes become common, the overview may need a clearer time-lane treatment instead of drawing every strategy directly between vision and outcomes.

## Step 2: Restyle the graph editor like Excalidraw

**Author:** main

### Prompt Context

**Verbatim prompt:** Also I want the style of the ui to be more like excalidraw
**Interpretation:** Keep the existing editor behavior but move the visual design away from the dark dashboard style and toward a hand-drawn canvas.
**Inferred intent:** Make the product graph feel more like a collaborative sketching surface where strategy and delivery nodes can be scanned visually.

### What I did

I restyled `/src/outcome_engineering/templates/graph.html` with a light paper background, dotted canvas texture, sketch-like borders, pastel node colors, softer side panels, and hand-drawn-feeling buttons and chips. I added an SVG sketch filter, node fill overlays, rounded irregular node strokes, and deterministic edge wobble through `sketchOffset(a, b)` so connections feel less rigid without becoming random on every render. I also changed the header Vision and Strategy buttons to select the corresponding graph nodes when present.

### Why

The previous dark UI read like an operations dashboard. The requested Excalidraw direction fits the product graph better as a thinking and mapping surface, especially now that vision and strategy appear in the overview.

### What worked

The change stayed dependency-free and inside the existing single-file template. Deterministic edge offsets gave the graph a sketch quality while keeping layout stable for repeated renders and tests.

### What didn't work

No implementation failure occurred in this step. The main constraint was avoiding an external drawing library so `oe serve` remains dependency-free.

### What I learned

The template already centralizes node and edge primitives, so a broad visual change can be made without touching graph APIs or the CRUD handlers.

### What was tricky

The UI needs to look hand-drawn while still being readable at graph scale. I kept label sizes, stable node dimensions, and the existing fit/pan behavior intact rather than making the sketch effect overly decorative.

### What warrants review

Review the CSS variables and SVG primitives in `/src/outcome_engineering/templates/graph.html`, especially color contrast on the paper background and whether the edge wobble is subtle enough on dense graphs.

### Future work

If the UI later accepts third-party frontend assets, a proper rough drawing library could replace the lightweight SVG filter and deterministic path offsets.

## Step 3: Preserve zoom when selecting nodes

**Author:** main

### Prompt Context

**Verbatim prompt:** omg i love it. 

also, when you zoom in and click on a node, it zoom out agian. thats annoying.
**Interpretation:** Node selection should not reset the user's current pan and zoom.
**Inferred intent:** Keep exploration fluid; clicking nodes should inspect content without destroying the viewport the user intentionally set.

### What I did

I changed `/src/outcome_engineering/templates/graph.html` so `render()` accepts `{ fitView = false }`. The overview and focus renderers now only rebuild SVG content; the shared render function calls `fit()` only when explicitly requested and otherwise reapplies the existing `state.view`. I left `fitView: true` on layout-changing actions such as initial load, focus changes, overview navigation, collapse toggles, legend filters, and the Vision/Strategy header shortcuts. Plain node selection and blank-canvas deselection now preserve zoom and pan. I added `/tests/test_graph.py` coverage that locks in the viewport-preserving render contract.

### Why

The previous implementation called `fit()` at the end of every overview or focus render, so a selection highlight caused the graph to recenter and zoom even though layout had not changed.

### What worked

Separating layout rendering from viewport fitting was enough; no graph model or API changes were needed.

### What didn't work

No command or implementation failure occurred during this step.

### What I learned

Selection state and layout state were coupled through the render side effect. Keeping fit behavior explicit makes future interactions easier to reason about.

### What was tricky

Some rerenders still should fit, especially entering an outcome focus view or hiding/showing node kinds. The fix needed to preserve zoom for inspection clicks without making layout-changing actions leave the user looking at an empty or badly framed canvas.

### What warrants review

Review `/src/outcome_engineering/templates/graph.html` around `render`, `enterFocus`, `goOverview`, `toggleCollapse`, and legend filtering. Validate manually by zooming in, clicking a node, and confirming the viewport stays put.

### Future work

The UI could eventually remember separate viewport positions for overview and each focused outcome, but preserving the current viewport on selection fixes the immediate interaction bug.
