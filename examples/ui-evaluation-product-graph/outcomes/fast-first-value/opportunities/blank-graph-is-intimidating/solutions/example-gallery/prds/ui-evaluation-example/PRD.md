# UI Evaluation Example

```yaml
type: prd
id: prd.ui-evaluation-example
status: backlog
```

## Problem

UI work needs a realistic graph fixture with enough breadth and depth to reveal layout, editing, and navigation issues.

## User Stories

- As a UI developer, I can load a comprehensive graph without hand-building files.
- As a reviewer, I can inspect statuses, ICP edges, nested opportunities, PRDs, and assumption tests.
- As a maintainer, I can regenerate the fixture from the CLI.

## Acceptance Criteria

- The example includes multiple ICPs and outcomes.
- The example includes nested opportunities and mixed solution depth.
- The example includes shipped, active, planned, blocked, and backlog statuses.
- The example validates with `oe validate`.
