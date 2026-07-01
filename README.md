# Outcome Engineering

Outcome Engineering turns messy product thinking into a repo-native product graph that humans and agents can challenge, trace, and update.

## CLI

The Python package is `outcome-engineering`. The command is `oe`.

```sh
uv run oe install --skills --force
uv run oe validate product
uv run oe tree product
uv run oe list outcomes --root product
uv run oe context outcome.messy-product-assumptions --root product
uv run oe new strategy <slug> --root product
uv run oe new icp <slug> --root product
uv run oe new opportunity <slug> --root product --under outcome.<slug>
uv run oe serve product
```

Use `product/` as the graph root.

`oe serve` starts a local web UI for visualizing **and editing** the graph as a
team. It opens on an Excalidraw-like strategic overview with vision, strategy,
ICPs, and outcomes as visible nodes; clicking an outcome focuses into its full
trace subtree (opportunities → solutions → assumption tests / PRDs) with
collapsible branches and node content in a side panel. From the side panel you
can edit a node's marker file, add child nodes (the UI only offers placements
the model allows), and delete nodes (a node with descendants needs an explicit
cascade). Every change writes straight back to the marker files on disk, so
collaboration happens through git like everything else in the repo. The server
is dependency-free (Python stdlib) and binds to loopback by default; use
`--host`/`--port` to change that and `--no-open` to skip launching a browser.

## Hosted read-only graph

The package also includes a FastAPI app for hosting one read-only graph behind
external access control:

```sh
OE_GRAPH_ROOT=product uv run uvicorn outcome_engineering.hosted:app --host 0.0.0.0 --port 8000
```

The hosted app exposes HTTP equivalents of the read-only CLI workflows:
`/api/graph`, `/api/validate`, `/api/nodes`, `/api/nodes/{selector}`,
`/api/nodes/{selector}/trace`, and `/api/nodes/{selector}/context`.
Context responses include both structured JSON and markdown. The app does not
register create, edit, delete, or reorganization routes; authentication is
expected to live in the deployment/proxy layer. `Dockerfile.hosted` builds a
single-graph deployable that reads the bundled `product/` directory, suitable
for redeploying from CI on each push to `main`.

Graph metadata lives in Markdown frontmatter. Fenced YAML metadata blocks are invalid.

An ICP (ideal customer profile) is the "who" the graph serves. A graph can have one or more, and they live in the top-level `product/icps/` collection. ICPs are not part of the outcome → opportunity → solution trace chain; instead outcomes and opportunities reference the ICPs they serve by listing `icp.<slug>` ids in frontmatter.

Strategy is top-level product context. A simple graph can keep its current strategy in `product/STRATEGY.md`; additional historical or planned strategies can live under `product/strategies/<slug>/STRATEGY.md`. Strategies declare `name`, `starts`, and `ends` in frontmatter, and `oe validate` rejects missing strategy names or dates, invalid ranges, explicit strategy status, or overlapping strategy periods.

## Docs

- [product/VISION.md](product/VISION.md)
- [product/STRATEGY.md](product/STRATEGY.md)
