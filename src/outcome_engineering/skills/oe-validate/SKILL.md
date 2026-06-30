---
name: oe-validate
description: Use when asked to validate an Outcome Engineering product graph, explain validation errors, or fix graph structure so `uv run oe validate product` passes.
---

# OE Validate

Run deterministic commands first; only reason after seeing real output.

## Workflow

1. From the project containing `product/`, validate:

```sh
uv run oe validate product
```

2. If validation passes, report that the graph is structurally valid.

3. If validation fails:
- quote the failing command and error summary
- identify affected files
- propose the smallest patch
- ask for approval before editing

4. After approval, apply the patch and rerun:

```sh
uv run oe validate product
```

Stop when validation passes or when a required product decision is missing.
