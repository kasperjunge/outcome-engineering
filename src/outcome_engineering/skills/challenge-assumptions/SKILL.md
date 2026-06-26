---
name: challenge-assumptions
description: Use this skill whenever the user wants to challenge assumptions, test a product idea, reduce value/usability/feasibility/viability risk, avoid overbuilding, or turn messy product thinking into assumptions and learning steps. This skill should use the oe-cli skill and the oe CLI whenever a product graph is present or should be created.
---

# Challenge Assumptions

Help the user expose what must be true before they build too much.

## Workflow

1. Use the `oe-cli` skill.
2. Check for a graph:
   ```sh
   test -d product && uv run oe validate product
   ```
3. If a graph exists, inspect it:
   ```sh
   uv run oe tree product
   ```
4. Read any relevant graph context before judging the idea:
   ```sh
   uv run oe context <node-id-or-slug> --root product
   ```
5. Identify the riskiest assumptions in plain language.
6. Group assumptions by product risk when useful: value, usability, feasibility, viability.
7. Propose graph changes, but do not silently mutate product truth. Humans approve.

## Output

Keep the response concise:

- The likely hidden assumptions.
- The riskiest assumption to learn about next.
- Suggested graph nodes or edits, if useful.
- The next learning step.

Prefer useful partial graphs over complete graphs.
