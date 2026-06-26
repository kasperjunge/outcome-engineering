---
name: challenge-assumptions
description: Use this skill whenever the user wants to challenge assumptions, test a product idea, reduce value/usability/feasibility/viability risk, avoid overbuilding, or turn messy product thinking into assumptions and learning steps. Listen first for the idea, feature, PRD, assumption, or messy product text the user wants challenged. Use oe-cli and any product graph as quiet background context when present, not as the visible center of the response.
---

# Challenge Assumptions

Help the user expose what must be true before they build too much.

## Workflow

1. Listen for the product thinking the user wants challenged: an idea, feature, PRD, assumption, solution, opportunity, or messy pasted notes.
2. If the user has not provided anything to challenge, ask for it directly and stop. Do not inspect or explain graph structure first.
3. Use the `oe-cli` skill.
4. Quietly check for a graph:
   ```sh
   test -d product && uv run oe validate product
   ```
5. If a graph exists, use it only as background context:
   ```sh
   uv run oe tree product
   ```
6. Read relevant context only when it helps judge the user's actual input:
   ```sh
   uv run oe context <node-id-or-slug> --root product
   ```
7. Identify the riskiest assumptions in plain language.
8. Group assumptions by product risk when useful: value, usability, feasibility, viability.
9. Propose product graph changes only when useful, and keep them secondary. Do not silently mutate product truth. Humans approve.

## Interaction Principles

- The user cares about getting their product thinking challenged, not about graph mechanics.
- Do not narrate graph validation, tree structure, node ids, or CLI steps unless the user asks.
- Mention the graph only when it materially changes the product judgment or when suggesting a concrete edit.
- Keep the answer anchored in the user's words and decision, not in the repository structure.

## Output

Keep the response concise:

- The likely hidden assumptions.
- The riskiest assumption to learn about next.
- The next learning step.
- Suggested graph nodes or edits, only if useful.

Prefer useful partial graphs over complete graphs.
