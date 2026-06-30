---
type: prd
id: prd.experimental-flywheel-graph-mvp
status: draft
---

# Experimental flywheel graph MVP

## Problem

The first user and strategy-minded early builders can capture vision, strategy, outcomes, opportunities, solutions, assumptions, and PRDs in Outcome Engineering, but they do not yet have a structured place to define the reinforcing strategic motion behind those choices.

The normal product graph is intentionally traceable and mostly hierarchical. A flywheel is different: it is a causal loop. Builders need a way to capture that loop without confusing it with the normal outcome -> opportunity -> solution trace chain.

This PRD defines the first experimental version of a flywheel graph surface: optional, strategy-level, visually inspectable, and useful as agent context. The normal product graph must remain fully useful without flywheel content.

## User Stories

- As a solo builder, I can create a strategy flywheel so I can explain how my product or business is supposed to build momentum.
- As a solo builder, I can define flywheel nodes so I can name the drivers of strategic momentum.
- As a solo builder, I can define directed causal links between flywheel nodes so I can explain why one step strengthens the next.
- As a solo builder, I can view the flywheel as a circular graph so I can inspect the whole strategic loop at once.
- As a solo builder, I can read and edit the flywheel in a repo-native artifact so the strategy logic remains durable and agent-legible.
- As an agent, I can inspect the flywheel as optional strategy context so I can critique causal links and relate product work back to strategic momentum.

## Acceptance Criteria

- A product graph can include an optional experimental flywheel artifact without making flywheels required for normal graph validation.
- The flywheel artifact supports a title, short description, nodes, directed edges, and edge explanations.
- Each flywheel edge requires a causal explanation, not only a source and target.
- The graph UI exposes a flywheel view when a flywheel artifact exists.
- The flywheel view renders nodes in a loop and shows the directed relationships between them.
- Selecting a flywheel node or edge shows its text content in the side panel.
- The flywheel remains visually and conceptually separate from the normal product trace graph.
- Agent-facing context can include the flywheel when strategy context is requested.
- Empty or missing flywheel data does not break `oe validate`, `oe tree`, or the existing graph UI.
- Users can ignore flywheels entirely and still create, inspect, validate, and use the normal product graph.

## Proposed Artifact Format

Use a directory-backed markdown graph so the flywheel feels native to Outcome Engineering while staying separate from the normal product graph.

```text
product/
  flywheels/
    strategy/
      FLYWHEEL.md
      nodes/
        <node-slug>/
          FLYWHEEL_NODE.md
```

`FLYWHEEL.md` describes the whole flywheel. Each `FLYWHEEL_NODE.md` describes one causal force in the loop. Directed links live in node frontmatter as `next`, and the body explains why that node creates the next step.

Example node:

```md
---
type: flywheel-node
id: flywheel-node.clearer-product-graph
next:
  - flywheel-node.agent-legible-intent
status: experimental
---

# Clearer product graph

Outcome Engineering turns messy product thinking into traceable product intent.

## Why this creates the next step

A clearer graph gives agents stable product context they can inspect, challenge, and use during implementation.
```

## Non-Goals

- Do not make flywheels a required part of every Outcome Engineering graph.
- Do not turn flywheel nodes into outcomes, opportunities, solutions, or PRDs.
- Do not support multiple flywheels until the single-flywheel workflow proves useful.
- Do not validate whether the flywheel is strategically good; validation should only check structure.

## Open Questions

- Should the first artifact be `product/FLYWHEEL.md` or `product/flywheels/<slug>/FLYWHEEL.md`?
- Should the flywheel be edited directly in markdown first, visually in the UI first, or both in the first version?
- Should the flywheel appear as a tab in the overview UI, a strategy-node detail mode, or a separate route?
- How much agent critique should be built into the feature versus left to skills and prompts?
