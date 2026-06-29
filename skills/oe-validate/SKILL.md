---
name: oe-validate
description: Use when asked to update Outcome Engineering, validate an OE product graph, check whether a graph is out of sync with the installed OE CLI, or propose/fix OE validation errors.
---

# OE Validate

Run deterministic commands first; only reason after seeing real output.

## Workflow

1. From the project containing `product/`, update OE:

```sh
uv lock --upgrade-package outcome-engineering
uv sync
```

If `outcome-engineering` is not declared, propose adding it as a dependency.

2. Validate:

```sh
uv run oe validate product
```

3. If validation passes, report that the graph is compatible with the installed OE version.

4. If validation fails:
- quote the failing command and error summary
- identify affected files
- propose the smallest patch
- ask for approval before editing

5. After approval, apply the patch and rerun:

```sh
uv run oe validate product
```

Stop when validation passes or when a required product decision is missing.
