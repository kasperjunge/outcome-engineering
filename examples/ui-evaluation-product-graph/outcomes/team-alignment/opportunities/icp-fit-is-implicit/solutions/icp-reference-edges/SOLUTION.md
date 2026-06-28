# ICP Reference Edges

```yaml
type: solution
id: solution.icp-reference-edges
status: shipped
```

Render ICP references as non-structural edges so the UI distinguishes who a node serves from the trace hierarchy.

## Product Risks

- Value: users may not care about ICPs in early graphs.
- Usability: extra edges can create visual clutter.
- Feasibility: the graph serializer must keep structural and ICP edges separate.
- Viability: ICP links support positioning and sales conversations later.

## Assumptions

- Users can understand two edge types when they are visually distinct.
- ICP links are useful at outcome and opportunity levels, but noisy below that.
