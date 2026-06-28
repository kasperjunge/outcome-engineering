# Traceable PRD Panel MVP

```yaml
type: prd
id: prd.traceable-prd-panel-mvp
status: ready
```

## Problem

Reviewers cannot quickly inspect why a PRD exists or which assumptions it depends on.

## User Stories

- As a product lead, I can select a PRD and see its full trace.
- As an engineer, I can inspect assumptions before proposing a scope cut.
- As a reviewer, I can jump from the PRD to the exact opportunity it addresses.

## Acceptance Criteria

- The panel lists all ancestors from outcome to solution.
- The panel shows sibling assumption tests and their statuses.
- The PRD body remains editable without losing scroll position.
- The UI handles long markdown without overlapping graph controls.
