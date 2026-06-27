# Diary: Graph visualization UI

Added `oe viz`, a command that renders the product graph as a single self-contained HTML file an agent can generate on the fly.

## Step 1: Design and build the viz command

**Author:** main

### Prompt Context

**Verbatim prompt:** I'm considering making a UI of the graph that the agent can generate on the fly as a single html file when needed to visualize the graph. Please research the process and let me know how you think we could design such a ui.

Followed by a discussion of whether to show everything in one view or factor it into separate views (per-outcome views plus a top-level vision/strategy/ICP view), then: give it a shot.

**Interpretation:** Build a single-file HTML visualization of the discovered product graph, factored by level rather than into separate artifacts.

**Inferred intent:** Make the invisible graph structure concrete and exciting, which the strategy names as an adoption driver.

### What I did

I added `viz.py` (`build_graph_payload` + `render_html`), a self-contained HTML template under `templates/`, and the `oe viz` command. The command validates first like the other commands, serializes the graph, and writes one HTML file (or stdout with `-o -`).

The payload reuses `discover_nodes` and separates the model's two edge meanings: structural parent→child trace edges and many-to-many ICP reference edges. Vision and strategy are returned as prose context, not graph nodes.

### Why

The strategy doc calls a lightweight visual graph UI important because it makes structure concrete. Keeping it a single dependency-free file means an agent can emit it anytime and it opens straight from `file://`.

### What worked

The two-level model fell out of the data naturally. The graph is a strict tree of outcome subtrees plus ICP cross-links, so the overview shows ICPs + outcomes, and clicking an outcome focuses into its trace subtree. The renderer is hand-rolled SVG with pan/zoom, collapse/expand, a kind legend, and a markdown side panel — no vendored library needed.

### What didn't work

The real `product/` graph only has one outcome and one ICP, so I exercised the deeper tactical view against the generated example graph (12 nodes) instead.

### What I learned

Because the two edge types never need to share a layout (ICP links live at the strategic level, the subtree is a pure tree at the tactical level), a general DAG layout engine is unnecessary; a simple layered tree layout is enough.

### What was tricky

Keeping the markdown rendering safe without a dependency: the panel escapes input first, then formats a known subset (headings, lists, code, bold/inline-code).

### What warrants review

Whether the single-canvas-with-focus interaction is enough, or whether the tactical level should graduate into a distinct scene. Also whether ICPs should be filterable in the overview as the graph grows.

### Future work

Search/jump to node, trace-path highlighting from root to a selected node, and status-based filtering.
