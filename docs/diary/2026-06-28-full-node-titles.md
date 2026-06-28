# Diary: Show full graph node titles

Fix the graph UI so node titles are visible in full instead of being shortened with an ellipsis.

## Step 1: Wrap SVG node titles

**Author:** main

### Prompt Context

**Verbatim prompt:** it is annoying that you cant see the full title in the nodes. please make sure you can see the entire title [Image #1]
**Interpretation:** The graph node cards in the served UI truncate long titles, making outcome names hard to read.
**Inferred intent:** Make the visual graph usable without needing the detail panel just to identify nodes.

### What I did

I inspected `/src/outcome_engineering/templates/graph.html`, confirmed labels used `truncate(n.title, 22)`, and replaced that with `wrapTitle(title)` plus SVG `tspan` lines. I widened nodes, made node height derive from wrapped title line count, moved toggle and edge endpoints to use the dynamic node height, and increased row and column spacing to fit larger cards. I updated `/tests/test_graph.py` so the focus toggle assertion matches dynamic height and added a regression check that full-title wrapping remains present and `truncate(n.title` does not return.

I ran `uv run oe validate product` before and after the code change, `uv run pytest tests/test_graph.py`, and a Playwright render check against `uv run oe serve examples/star --host 127.0.0.1 --port 8765 --no-open`. The render check confirmed STAR outcome titles like `Digital Infrastruktur Skaber Sammenhæng`, `Reformen Bliver Til Lokal Praksis`, and `Viden Driver Bedre Beslutninger` appear as full wrapped title lines.

### Why

The old fixed-width, single-line title intentionally discarded the rest of each title. Wrapping keeps the graph compact while preserving the complete node title in the card.

### What worked

The existing SVG drawing functions were centralized enough that the fix could stay inside the node and edge primitives. The graph already refits the viewport after render, so larger nodes were automatically brought into view.

### What didn't work

My first Playwright CLI verification command used the wrong `eval` form and failed with `Unknown command: await new Promise(r => setTimeout(r, 300)); JSON.stringify([...document.querySelectorAll('g.node')].map(g => ({text:g.textContent, tspans:[...g.querySelectorAll('tspan')].map(t=>t.textContent), box:g.querySelector('rect.box')?.getBBox()})).slice(0,10))`. I reran it with `playwright-cli run-code`, which worked.

### What I learned

The current worktree already had unrelated graph template changes compared with `HEAD`, including removed legend and strategy/vision buttons. I left those intact and made the title fix on top of the current file state.

### What was tricky

SVG text does not wrap automatically, so the title has to be split into explicit `tspan` lines. Edge routing and collapse toggles also depended on the old fixed `NODE_H`, so they needed to move with the dynamically computed node height.

### What warrants review

Review `/src/outcome_engineering/templates/graph.html` around `wrapTitle`, `nodeHeight`, `drawNode`, and `edgePath`. Validate with `uv run oe serve examples/star --host 127.0.0.1 --port 8765 --no-open` and confirm long node titles are visible in overview and focus views.

### Future work

If users create extremely long prose titles, the graph will keep showing the full title by making taller nodes. A later layout pass could make row spacing depth-aware so unusually tall nodes get more vertical room only where needed.
