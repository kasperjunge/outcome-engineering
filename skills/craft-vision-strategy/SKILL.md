---
name: craft-vision-strategy
description: Use this skill whenever the user wants to create or refine product vision, strategy, outcomes, focus, positioning, or the top of an Outcome Engineering graph. This skill should use the oe-cli skill and the oe CLI whenever a product graph is present or should be created.
---

# Craft Vision And Strategy

Help the user make the top of the graph clear enough to guide work.

## Workflow

1. Use the `oe-cli` skill.
2. Check for a graph:
   ```sh
   test -d product && uv run oe validate product
   ```
3. If a graph exists, read the current top-level intent:
   ```sh
   uv run oe tree product
   ```
   Also read `product/VISION.md` and `product/STRATEGY.md` when present.
4. Interview only until the strategic shape is clear enough. Ask one question at a time.
5. Draft concise vision/strategy text.
6. Propose graph changes, but do not silently mutate product truth. Humans approve.
7. Validate after approved graph edits:
   ```sh
   uv run oe validate product
   ```

## Output

Keep the response concise:

- Vision draft.
- Strategy draft or strategic choices.
- Open questions that actually block clarity.
- Suggested graph edits, if useful.

Do not turn strategy into roadmap planning unless the user asks.
