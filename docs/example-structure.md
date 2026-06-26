# Example Structure

This repository includes a small generator for an example Outcome Engineering product graph.

Run:

```sh
uv run oe create-example --force
uv run oe validate examples/delegation-product-graph
uv run oe tree examples/delegation-product-graph
uv run oe list solutions --root examples/delegation-product-graph
```

The script writes:

```text
examples/delegation-product-graph/
```

The example uses a filesystem-native graph convention:

- A graph node is a directory with a canonical marker file, such as `OUTCOME.md`, `OPPORTUNITY.md`, `SOLUTION.md`, `ASSUMPTION.md`, `EXPERIMENT.md`, or `PRD.md`.
- Relationship directories, such as `opportunities/`, `solutions/`, `assumptions/`, `experiments/`, and `prds/`, define the edge from a parent node to child nodes.
- Assumptions can live under opportunities or solutions.
- Experiments can only live under assumptions.
- Supporting files can live beside the marker file inside the node directory.

Example path:

```text
outcomes/delegation-confidence/
  opportunities/agents-lack-safe-access-to-tools/
    solutions/agent-central/
      PRD.md
```

This path says that `agent-central` is a solution bet for the opportunity `agents-lack-safe-access-to-tools`, which supports the outcome `delegation-confidence`.

Trace a node:

```sh
uv run oe trace solution.agent-central --root examples/delegation-product-graph
```

Show a node:

```sh
uv run oe show solution.agent-central --root examples/delegation-product-graph
```

Print agent context for a node:

```sh
uv run oe context solution.agent-central --root examples/delegation-product-graph
```

Create a new node:

```sh
uv run oe new opportunity my-opportunity --root product --under outcome.my-outcome
```

For real repositories, use `product/` as the stable product graph root.

Install the bundled agent skill:

```sh
uvx outcome-engineering install --skills
uvx outcome-engineering install --skills=agents
```
