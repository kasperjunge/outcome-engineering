# Diary: Hosted read API

This records the implementation of the hosted read-only HTTP surface for one Outcome Engineering product graph.

## Step 1: Add shared read service and hosted FastAPI app

**Author:** main

### Prompt Context

**Verbatim prompt:** looks great, go
**Interpretation:** Implement the approved plan for a hosted read-only web/API deployable that serves CLI-equivalent read functionality over HTTP.
**Inferred intent:** Make the hosted graph more than a one-off UI by decoupling read behavior from interface code so the CLI, hosted web/API, and possible future MCP can share graph read functionality.

### What I did

I created the worktree `/.worktrees/hosted-read-api` on branch `hosted-read-api` before editing. I added `/src/outcome_engineering/read.py` as a shared read service for validation payloads, graph payloads, node listing, node display, trace, context, source metadata, and selector resolution errors.

I updated `/src/outcome_engineering/serve.py` so the existing local editable stdlib server reuses the shared graph payload builder instead of owning a duplicate serialization path. I added `/src/outcome_engineering/hosted.py`, a FastAPI app that serves the read-only graph UI and the read-only endpoints `/api/graph`, `/api/validate`, `/api/nodes`, `/api/nodes/{selector}`, `/api/nodes/{selector}/trace`, and `/api/nodes/{selector}/context`. I added `/Dockerfile.hosted` for a single-graph hosted deployable that reads bundled `/product` and expects external proxy/deployment auth.

I updated `/src/outcome_engineering/templates/graph.html` with an `OE_READ_ONLY` switch. The hosted app renders it as read-only, hides top-level add buttons, suppresses node edit/create/delete controls, and does not expose mutation routes. Local `oe serve` still renders the editable version.

I moved `oe context` in `/src/outcome_engineering/cli.py` onto the shared read service's markdown context output. I added FastAPI and uvicorn runtime dependencies, an httpx dev dependency for FastAPI test clients, and refreshed `/uv.lock`. I documented the hosted app and HTTP API in `/README.md`.

### Why

The hosted web app and possible future MCP server need the same read behavior as the CLI without each interface reimplementing graph traversal, context assembly, response shape, or source metadata. Keeping hosted mutation routes absent also makes the app read-only even if external auth is misconfigured.

### What worked

The existing graph primitives were already clean enough to support a read service without changing the graph model. The current graph UI only needed a small read-only switch because the visualization and node inspection behavior were already separate from the mutation API calls.

### What didn't work

The first full test run failed:

```text
uv run pytest tests/test_graph.py -q
...
FAILED tests/test_graph.py::test_hosted_app_reports_selector_and_validation_errors
E       assert 200 == 503
```

The test used an empty directory as an invalid graph root, but the current validator treats an existing empty graph directory as structurally valid. I changed the fixture to use a missing graph root, which matches the existing validator behavior.

FastAPI's test client also emitted this warning during tests:

```text
StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
```

It does not fail the suite, but it may require a dependency adjustment later if FastAPI/Starlette changes their preferred test client dependency.

### What I learned

The current local server had two separable responsibilities: graph serialization and local mutation. Pulling serialization into `/src/outcome_engineering/read.py` let hosted read-only behavior reuse the useful part without carrying over create, edit, and delete routes.

The graph model currently allows an empty graph root. Hosted invalid-graph behavior should therefore be based on `validate(root)` rather than an assumption that a graph must contain nodes.

### What was tricky

REST paths for selectors are awkward because local CLI selectors can include filesystem paths. For v1, the hosted routes support node id and slug selectors in the path, which covers the intended public-after-auth API. Filesystem path selectors remain a CLI feature.

Keeping local `oe serve` editable while serving the same template read-only required server-side template substitution instead of forking the UI file.

### What warrants review

Review `/src/outcome_engineering/read.py` for the shared read contract, `/src/outcome_engineering/hosted.py` for hosted API behavior and error status choices, and `/src/outcome_engineering/templates/graph.html` for the read-only switch. Validate with `uv run pytest`, `uv run ruff check .`, `uv run ty check .`, and `uv run oe validate product`.

### Future work

The hosted API currently supports id and slug selectors in route paths. If hosted clients need marker-file/path selectors, add query-parameter selector support instead of making the route path greedy. CI deployment wiring still needs to be added wherever the production deployment is managed.
