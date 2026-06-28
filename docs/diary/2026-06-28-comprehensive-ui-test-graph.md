# Diary: comprehensive UI test graph

Generated a comprehensive Outcome Engineering product graph fixture for evaluating the visual editor, and served it locally for review.

## Step 1: Add comprehensive graph generator

**Author:** main

### Prompt Context

**Verbatim prompt:** in outcome-engineerin, please genrate a quite comprehensive test product graph i can use to evaluate the ui

**Interpretation:** Create a substantial product graph fixture inside the `outcome-engineering` repo for UI evaluation.

**Inferred intent:** Provide a realistic graph with enough node variety, depth, statuses, ICP links, PRDs, assumption tests, and supporting files to exercise the graph UI.

### What I did

I created a `comprehensive-test-graph` worktree from `main` because the main checkout already had local edits in `/src/outcome_engineering/graph.py` and `/src/outcome_engineering/model.py`. I extended `/src/outcome_engineering/example.py` with a reusable comprehensive example generator, added `--comprehensive` support to `/src/outcome_engineering/cli.py` and `/scripts/create_example_product_graph.py`, documented the command in `/README.md`, and added tests in `/tests/test_graph.py`. I generated the fixture at `/examples/ui-evaluation-product-graph`.

### Why

A generator keeps the UI fixture reproducible and makes it easier to refresh as graph rules change, while the checked-out generated graph gives the current UI something immediate to serve.

### What worked

`uv run oe create-example --comprehensive --output examples/ui-evaluation-product-graph --force` generated the graph, and `uv run oe validate examples/ui-evaluation-product-graph` reported it as valid. The generated graph includes four ICPs, three outcomes, nested opportunities, multiple solutions, PRDs, assumption tests, status variation, ICP reference edges, and supporting evidence files.

### What didn't work

The first test run failed because the initial comprehensive graph had 38 nodes while the test expected at least 40:

```text
AssertionError: assert 38 >= 40
```

I fixed that by adding an assumption test and PRD under the `example-gallery` solution rather than weakening the test. A later HTTP check used `python`, which is not on this shell's path:

```text
zsh:1: command not found: python
curl: (23) Failure writing output to destination, passed 16384 returned 0
```

I reran the check with `uv run python`.

### What I learned

The graph payload is large enough to exercise both structural and ICP edge rendering: the generated API payload has 40 nodes and 42 edges. The existing graph model in this checkout uses `assumption-test` nodes under `assumption-tests/`, so the fixture follows that convention.

### What was tricky

The fixture needed enough breadth for the strategic overview and enough nested depth for focused outcome review, without introducing invalid relationship folders or unsupported experiment nodes.

### What warrants review

Review `/src/outcome_engineering/example.py` for content shape and whether the example should be bundled, generated only, or both. Validate with `uv run pytest`, `uv run oe validate examples/ui-evaluation-product-graph`, and the served UI.

### Future work

If the UI adds more visual states, extend the generated fixture with nodes that exercise those states explicitly rather than relying on ad hoc manual edits.

## Step 2: Serve the generated graph

**Author:** main

### Prompt Context

**Verbatim prompt:** when your done, start a serve ui for the graph so i can view it

**Interpretation:** Start the Outcome Engineering web UI against the generated comprehensive graph after implementation is complete.

**Inferred intent:** Let the user immediately inspect the fixture in the UI.

### What I did

I started `uv run oe serve examples/ui-evaluation-product-graph --host 127.0.0.1 --port 8765 --no-open` from the worktree. I verified `/api/graph` with `curl -fsS http://127.0.0.1:8765/api/graph | uv run python -c 'import json,sys; data=json.load(sys.stdin); print(len(data["nodes"]), "nodes"); print(len(data["edges"]), "edges"); print(data["nodes"][0]["id"])'`.

### Why

Serving the generated fixture makes the UI evaluation graph available immediately without requiring the user to run setup commands.

### What worked

The server started successfully at `http://127.0.0.1:8765/`, and the API check returned `40 nodes`, `42 edges`, and `icp.agency-delivery-lead` as the first node id.

### What didn't work

No server startup issue occurred.

### What I learned

Port `8765` was available and is serving the worktree copy of the generated graph.

### What was tricky

The server process needs to remain running in the active session, so it should not be stopped until the user is done reviewing.

### What warrants review

Open `http://127.0.0.1:8765/` and inspect overview density, focused outcome navigation, ICP edge rendering, status display, and side-panel markdown for long node content.

### Future work

If UI review reveals layout blind spots, add targeted fixture branches that reproduce them.

## Step 3: Add simulated Boligsiden graph

**Author:** main

### Prompt Context

**Verbatim prompt:** this is great. Try to also make an example that fits https://www.boligsiden.dk/ . research the product before you start and build a graph where you simulate/esitmiate/guess everything

**Interpretation:** Research Boligsiden from public product surfaces, then create a second example product graph that fits Boligsiden while clearly treating strategy, metrics, and priorities as simulated estimates.

**Inferred intent:** Use a real product domain to evaluate whether the graph UI can handle a consumer marketplace/search product with buyers, sellers, market data, and estate-agent relationships.

### What I did

I researched public Boligsiden surfaces and modeled it as a Danish housing decision product spanning property search, listing context, market transparency, seller readiness, and estate-agent discovery. I added `/src/outcome_engineering/example.py` support for a `boligsiden` fixture, exposed it through `/src/outcome_engineering/cli.py` and `/scripts/create_example_product_graph.py`, documented `uv run oe create-example --boligsiden --output examples/boligsiden-product-graph --force` in `/README.md`, and added validation/payload tests in `/tests/test_graph.py`. I generated `/examples/boligsiden-product-graph` and served it locally.

### Why

The UI needs examples that are not only Outcome Engineering self-references. Boligsiden is a useful domain because it has multiple ICPs, two-sided marketplace dynamics, search workflows, data trust concerns, and market-content-to-action loops.

### What worked

`uv run oe create-example --boligsiden --output examples/boligsiden-product-graph --force` generated a valid graph. `uv run oe validate examples/boligsiden-product-graph` passed, and `uv run pytest` passed with 33 tests. The served API returned `47 nodes`, `46 edges`, and `icp.active-home-buyer` as the first node.

### What didn't work

The first Boligsiden payload test expected at least 45 nodes, but the generated graph initially had 41:

```text
AssertionError: assert 41 >= 45
```

I added a buyer neighborhood watchlist branch and a seller listing-prep branch rather than lowering the test. My first patch matched similar solution-list shapes in the existing comprehensive graph and inserted the two Boligsiden branches there; I caught it by searching for the new slugs and moved them to the correct Boligsiden locations. Starting a UI server on `8766` failed because the port was occupied:

```text
OSError: [Errno 48] Address already in use
```

I started the Boligsiden graph on `8767` instead.

### What I learned

The current graph model is expressive enough for a marketplace/search product without adding new node kinds. ICP references at outcome level cover buyer, seller, market-follower, and estate-agent audiences, while opportunities and solutions can represent search relevance, comparison, local context, seller conversion, agent fit, data freshness, and insight-to-action flows.

### What was tricky

Because this is external research, the graph needed strong caveats. I added simulated status values, a research-boundary strategy section, and source-note supporting files so the fixture is useful without implying internal knowledge.

### What warrants review

Open `http://127.0.0.1:8767/` and review whether the graph reads like a plausible Boligsiden product model. Pay particular attention to whether the UI handles buyer/seller/market/agent ICP links and whether the product branches feel distinct enough to evaluate navigation.

### Future work

If this becomes a demo fixture, replace simulated evidence with more precise public references or internal discovery notes, and decide whether example variants should become a single `--variant` option rather than multiple flags.
