# ICP Edge Rendering

```yaml
type: prd
id: prd.icp-edge-rendering
status: shipped
```

## Problem

The UI needs to show which ICPs an outcome or opportunity serves without breaking the trace tree.

## User Stories

- As a user, I can see ICP relationships as distinct from structural hierarchy.
- As a reviewer, I can identify which outcomes serve a selected ICP.
- As an editor, I can inspect ICP references in the selected node body.

## Acceptance Criteria

- ICP nodes render in the overview.
- ICP edges use a separate edge type in the graph payload.
- ICP nodes list served-by references.
- Validation rejects unknown ICP references.
