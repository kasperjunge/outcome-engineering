---
type: solution
id: solution.hosted-read-only-product-graph
status: draft
---

# Hosted Read Only Product Graph

Provide a browser-accessible, authenticated, read-only view of an OE product graph.

Authorized users can open a website, log in, and view the graph from the repo's current `main` branch without running local commands. The view should make the graph useful for discussion: users can see the product vision, strategy, ICPs, outcomes, and connected lower-level work, and inspect what each node means.

The first version is intentionally read-only. Users cannot create, edit, delete, or reorganize graph nodes from the hosted website. Updates remain deliberate and repo-native through local files, terminal workflows, VS Code, or agents.

Success means a solo builder or small founder team can use the hosted graph as a shared reference point for product alignment.

## Product Risks

- Value: Users may not return to a hosted graph often enough if read-only access does not become part of their normal product rhythm.
- Usability: The graph must be understandable enough for collaborators who did not create it.
- Feasibility: The hosted view needs to reflect the current `main` branch reliably without making users think they can edit it there.
- Viability: Authentication and hosting should not turn a lightweight repo-native practice into heavyweight team process.

## Assumptions

- Browser access lowers the friction of revisiting the product graph.
- Small teams need shared visibility before they need shared editing.
- Read-only hosted access preserves the repo as the source of truth while still creating alignment value.
- Repeated read-only use is valuable enough to justify hosted access before collaboration or editing exists.
