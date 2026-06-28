# Context Command Contract

```yaml
type: prd
id: prd.context-command-contract
status: shipped
```

## Problem

Agents need deterministic context around a graph node before they can safely write product artifacts.

## User Stories

- As an agent, I can request context by id, slug, directory, or marker path.
- As a human reviewer, I can see the exact context an agent used.
- As a tool author, I can rely on a stable output shape.

## Acceptance Criteria

- The command validates the graph before printing context.
- The output includes trace, ICPs, children, supporting files, ancestor content, ICP content, and node content.
- Ambiguous selectors fail instead of guessing.
- Output order is deterministic.
