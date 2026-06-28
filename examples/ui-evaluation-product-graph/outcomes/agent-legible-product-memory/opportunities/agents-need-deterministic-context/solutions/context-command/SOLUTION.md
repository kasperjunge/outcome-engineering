# Context Command

```yaml
type: solution
id: solution.context-command
status: shipped
```

A CLI command prints deterministic context for a selected node, including trace, ICPs, children, supporting files, and marker content.

## Product Risks

- Value: context output may be too verbose for small tasks.
- Usability: selectors must be forgiving but not ambiguous.
- Feasibility: output must remain deterministic as graph rules evolve.
- Viability: agent workflows depend on stable command contracts.

## Assumptions

- Agents benefit from structured context before editing graph nodes.
- Humans can still read the output when debugging agent behavior.
