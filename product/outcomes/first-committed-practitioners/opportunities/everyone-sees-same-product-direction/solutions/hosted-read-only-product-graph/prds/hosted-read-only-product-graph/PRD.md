---
type: prd
id: prd.hosted-read-only-product-graph
status: draft
---

# Hosted Read Only Product Graph

## Problem

Solo builders and small founder teams can currently use the OE graph locally, but viewing it requires local repo and terminal workflow familiarity. That makes the graph harder to revisit casually and harder to share with co-founders or collaborators during product discussions.

When the graph is not available through a persistent, browser-accessible place, it risks becoming private product memory instead of shared product context. This weakens its ability to keep vision, strategy, outcomes, and active work aligned.

## Goal

A solo builder or small founder team can open a normal website, authenticate, and view the product graph from the repo's current `main` branch without running local commands.

The hosted graph should be useful as a read-only alignment surface for discussing product direction, inspecting current outcomes, and understanding how lower-level work connects back to larger product intent.

## User Stories

- As a solo builder, I want to open my product graph from a website so I can revisit product direction without local setup.
- As a founder, I want my co-founders to see the same product graph so we can align around vision, strategy, outcomes, and active work.
- As a graph owner, I want the hosted graph to be read-only so the repo remains the source of truth and graph updates stay deliberate.
- As an authorized collaborator, I want to inspect what each graph node means so I can participate in product discussions without needing to know the local OE workflow.

## Acceptance Criteria

1. The product graph is available through a browser-accessible website.
2. Unauthenticated visitors cannot see the graph.
3. Authorized users can log in with the company Google login.
4. The hosted graph reflects the product graph from the current `main` branch.
5. The hosted graph presents vision, strategy, ICPs, outcomes, and connected downstream nodes in a way suitable for discussion and alignment.
6. The hosted website does not allow users to create, edit, delete, or reorganize graph nodes.
7. Users can inspect graph content enough to understand what each node means and how it connects to the rest of the graph.
8. The experience makes clear that graph changes still happen through the repo-native workflow rather than through the hosted website.

## Scope

### In scope

- Authenticated browser access to a hosted read-only graph.
- Viewing the product graph from the repo's current `main` branch.
- Inspecting graph structure and node content.
- Supporting both solo-builder review and small-team founder alignment.

### Out of scope

- Editing the graph from the hosted website.
- Real-time collaboration features.
- Comments, annotations, notifications, or discussion threads.
- Viewing historical graph versions or branches other than `main`.
- Managing multiple independent product graphs.

## Risks

- Read-only access may not create enough repeated value without later collaboration or editing capabilities.
- Collaborators who did not create the graph may need more context than node content alone provides.
- If the hosted graph does not clearly reflect the current repo state, users may lose trust in it as an alignment surface.
