# Diary: full graph overview UI

This records the change from an overview-plus-focused-outcome graph UI to one full product graph view.

## Step 1: Render the whole product graph in overview

**Author:** main

### Prompt Context

**Verbatim prompt:** great. now in the ui i would like to see the entire graph in one view instead of having the splt view above and below outcome. Is this clear?
**Interpretation:** Replace the split overview/focused-outcome interaction with a single overview that renders the full graph at once.
**Inferred intent:** Make the product graph easier to inspect as a whole system without clicking into each outcome subtree.

### What I did

I created the `/ .worktrees/full-graph-view` worktree from `main`. I changed `/src/outcome_engineering/templates/graph.html` so overview lays out vision, strategy, ICPs, every outcome, and every descendant product graph node in one canvas. Outcome clicks now select the outcome and update the detail panel instead of switching into a separate focus layout. I removed the unused focus renderer and stale focus state. I updated `/tests/test_graph.py` so the template assertions check for the full graph renderer and the absence of the old focus mode.

I validated with:

```sh
uv run oe validate product
uv run pytest tests/test_graph.py -q
```

I also served the UI on `http://127.0.0.1:8766/` and verified with Playwright CLI that overview rendered 23 nodes, kept the breadcrumb as `overview`, and still showed all 23 nodes after selecting an outcome.

### Why

The previous UI used overview for high-level context and a separate focused subtree layout after clicking an outcome. That made the graph feel split. The requested behavior is to keep the whole product graph visible as the default overview.

### What worked

The existing tree layout logic from focus mode could be adapted into the overview renderer. The server payload already contains structural and ICP edges for the full graph, so no backend change was needed.

### What didn't work

`playwright-cli close` hung after verification and had to be interrupted. I cleaned up with:

```sh
playwright-cli kill-all || true
```

The cleanup reported:

```text
Killed daemon process 43847
Killed 1 daemon process.
```

### What I learned

The UI already had enough graph payload data to render the entire graph; the split behavior was entirely a frontend layout and interaction decision.

### What was tricky

The main risk was accidentally preserving the old focus behavior through outcome click handlers or create-node follow-up logic. Removing the dead focus renderer made the resulting behavior easier to reason about.

### What warrants review

Review `/src/outcome_engineering/templates/graph.html` for whether the full graph layout spacing works on larger product graphs. The current layout is tree-based and readable for the current graph, but wider examples may need smarter column compaction.

### Future work

If large graphs become hard to scan, add view controls for expand/collapse depth, filtering by node kind, or fit-to-subtree without returning to a separate focus mode.

