# Focus Mode

```yaml
type: solution
id: solution.focus-mode
status: active
```

A graph view that narrows to one outcome and its trace subtree while keeping ICP and strategy context visible.

## Product Risks

- Value: a narrowed graph may hide useful adjacent context.
- Usability: users need obvious controls for moving back to the overview.
- Feasibility: layout should stay stable when branches expand and collapse.
- Viability: focus mode must make the editor feel clearer than a file tree.

## Assumptions

- Teams mostly discuss one outcome at a time.
- A focused graph reduces cognitive load during product review.
