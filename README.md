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
uv run oe new icp <slug> --root product
uv run oe new opportunity <slug> --root product --under outcome.<slug>
```

Use `product/` as the graph root.

An ICP (ideal customer profile) is the "who" the graph serves. A graph can have one or more, and they live in the top-level `product/icps/` collection. ICPs are not part of the outcome → opportunity → solution trace chain; instead outcomes and opportunities reference the ICPs they serve by listing `icp.<slug>` ids in their yaml block.

## Docs

- [product/VISION.md](product/VISION.md)
- [product/STRATEGY.md](product/STRATEGY.md)
- [docs/agent-entry-points.md](docs/agent-entry-points.md)
