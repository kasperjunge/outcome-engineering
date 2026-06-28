# Live Validation Panel

```yaml
type: solution
id: solution.live-validation-panel
status: planned
```

Show validation issues directly in the UI after edits and structural mutations.

## Product Risks

- Value: validation issues may be rare in normal use.
- Usability: users need clear paths from issue to file and node.
- Feasibility: validation must run fast after each edit.
- Viability: better validation reduces support load for graph corruption.

## Assumptions

- Users will fix validation issues when shown exact paths.
- Allowing invalid marker edits is safer than rejecting and losing work.
