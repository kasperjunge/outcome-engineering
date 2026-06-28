# Diary: Editable graph UI (oe serve)

Replaced `oe viz` (a one-shot static HTML export) with `oe serve`, a local web UI that visualizes **and edits** the product graph: add, edit, remove, and visualize nodes as a team.

## Step 1: Replace viz with an editable server

**Author:** main

### Prompt Context

**Verbatim prompt:** Instead of oe viz I would like to replace it with oe serve that makes a editable ui version of the graph so you can add, remove, edit and visualize graph as a team.

Followed by a design discussion that settled two forks: "as a team" means **local tool + git as the collaboration layer** (not real-time multiplayer), and the static single-file export is **dropped** (serve fully replaces viz).

**Interpretation:** Turn the read-only visualization into a live editing surface backed by the filesystem, served locally, with git as the multiplayer.

**Inferred intent:** Let a team shape the graph directly in the picture instead of hand-editing marker files, while keeping the repo the single source of truth.

### What I did

I added `serve.py` (it absorbs `build_graph_payload` from the deleted `viz.py`) with a stdlib `http.server` JSON API over one graph root: `GET /api/graph`, `POST /api/nodes`, `PUT /api/nodes/{id}`, `DELETE /api/nodes/{id}`. I added `write_marker` and `delete_node` to `graph.py` alongside the existing `create_node`, swapped the `viz` command for `serve` in the CLI, and rewrote the HTML template from inlined-data + read-only into a fetch-driven editor (edit marker text, add legal child kinds, delete with cascade guard, validation surfaced inline).

### Why

The strategy calls a visual graph important because it makes structure concrete; making it editable closes the loop so the visual is also where you change the graph. Staying on the Python stdlib keeps the project's zero-dependency posture (it still only depends on `typer`).

### What worked

The reuse story carried most of the build: `create_node` already enforces the model's placement rules, `validate` already existed, and `build_graph_payload` and the SVG renderer moved over unchanged. The new code is the HTTP layer, two graph mutations, and the editing affordances. The payload gained a `schema.childKinds` map so the UI only ever offers placements the model allows.

### What didn't work

The first instinct was structured status/ICP form fields. Editing the raw marker file in one textarea turned out simpler and strictly more capable (the yaml block is right there), and it matches that the graph *is* the filesystem, so I went with that.

### What I learned

Create and delete can be strict (reject illegal moves with 400, leave the graph untouched), but a freeform marker edit shouldn't be: a mid-edit typo that fails validation still gets written, and the resulting issues are returned for the UI to show, so the user never loses work.

### What was tricky

Mutations had to rebuild client state safely — the indexes (`byId`, `childrenOf`, outcomes, icps) are rebuilt on every reload, and stale `focus`/`selected` ids are dropped so deleting the focused subtree falls back to the overview instead of erroring.

### What warrants review

Whether loopback-only with git as the collaboration layer is the right ceiling, or whether teams will want a shared hosted instance later. Also whether delete should offer to rewrite ICP references that pointed at a removed ICP, rather than leaving them for `validate` to flag.

### Future work

Re-parenting via drag (move a node's directory), node search/jump, and status-based filtering.
