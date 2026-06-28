# Validation Panel

```yaml
type: prd
id: prd.validation-panel
status: planned
```

## Problem

When a graph becomes invalid, users need to know what broke and where to fix it.

## User Stories

- As an editor, I can see validation issues immediately after saving a node.
- As a maintainer, I can navigate from an issue to the relevant file.
- As an agent, I can still use CLI validation as the source of truth.

## Acceptance Criteria

- The UI displays all validation issues returned by the API.
- Each issue includes a path and message.
- Issues refresh after create, edit, and delete actions.
- The UI remains usable when the graph has multiple simultaneous issues.
