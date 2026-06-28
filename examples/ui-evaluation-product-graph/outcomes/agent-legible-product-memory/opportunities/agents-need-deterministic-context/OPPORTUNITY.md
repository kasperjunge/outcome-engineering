# Agents Need Deterministic Context

```yaml
type: opportunity
id: opportunity.agents-need-deterministic-context
status: validated
```

Agents need a stable way to retrieve ancestors, children, ICPs, and supporting files around a node.

## Evidence

- Ad hoc file search produced inconsistent context windows.
- `oe context` reduced irrelevant file reads during PRD drafting.

## Known / Unknown

- Known: trace context is needed before editing or implementation work.
- Unknown: whether evidence files should be inlined, summarized, or only linked.
