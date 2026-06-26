---
name: challenge-product-intent
description: Use this skill whenever the user wants to check whether a PRD, spec, issue, feature idea, code change, acceptance test, or implementation plan traces back to product intent, outcomes, strategy, or vision. This skill should use the oe-cli skill and the oe CLI whenever a product graph is present.
---

# Challenge Product Intent

Help the user determine whether work is the right work.

## Workflow

1. Use the `oe-cli` skill.
2. Validate and inspect the graph:
   ```sh
   test -d product && uv run oe validate product
   uv run oe tree product
   ```
3. If the work references a graph node, load deterministic context:
   ```sh
   uv run oe context <node-id-or-slug> --root product
   ```
4. Trace upward from the artifact to opportunity, outcome, strategy, and vision.
5. Challenge gaps: unclear opportunity, output mistaken for outcome, weak evidence, risky assumptions, or low leverage.
6. Propose graph changes, but do not silently mutate product truth. Humans approve.

## Output

Keep the response concise:

- What outcome the work appears to serve.
- Whether the trace to vision is clear, weak, or missing.
- The main assumptions or evidence gaps.
- Whether this looks like the highest-leverage next work.
- Suggested graph edits, if useful.

Do not treat a valid graph as proof that the product judgment is good.
