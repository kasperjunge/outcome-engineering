# Diary: Time-bounded strategy validation

This records the change from a timeless singleton strategy toward strategy periods with derived activity.

## Step 1: Validate strategy periods

**Author:** main

### Prompt Context

**Verbatim prompt:** "yes, implement this and make it part of the validate routine of oe. also update the oe-cli skill if needed. when don commit and push all changes in the repo"
**Interpretation:** Add `starts` and `ends` as required strategy metadata, derive active strategy from those dates instead of a `status` field, validate that strategy periods do not overlap, update relevant skill/docs, then commit and push the repository changes.
**Inferred intent:** Make strategy time-aware without introducing user-facing lifecycle status, while keeping the current simple `product/STRATEGY.md` path valid and allowing future top-level strategy history.

### What I did

I updated `/src/outcome_engineering/model.py` and `/src/outcome_engineering/graph.py` so strategy can live as `product/STRATEGY.md` or under `/product/strategies/<slug>/STRATEGY.md`. The validator now requires strategy `starts` and `ends` fields, verifies ISO `YYYY-MM-DD` dates, rejects `status` on strategy because activity is derived, rejects `starts` after `ends`, and rejects overlapping strategy periods.

I added strategy creation support to the node model and kept strategy out of the visual graph placement schema for now because strategy is still rendered as prose context rather than a node-link graph item. I updated `/product/STRATEGY.md` with a current strategy period and refreshed `/product/outcomes/messy-product-assumptions/OUTCOME.md` so it no longer describes the old agent-skill wedge. I updated `/README.md`, `/skills/oe-cli/SKILL.md`, `/src/outcome_engineering/skills/oe-cli/SKILL.md`, `/skills/oe-grill/SKILL.md`, and `/src/outcome_engineering/skills/oe-grill/SKILL.md` to reflect time-bounded strategy behavior.

### Why

Strategy should represent a current strategic period, not a permanent truth. Deriving activity from dates avoids a redundant `status` field that could drift from the actual period.

### What worked

The existing fenced-yaml helper could be extended with a small scalar parser, so the change did not require adding a YAML dependency. The existing validation pattern also made it straightforward to add strategy-specific issues alongside ICP reference and placement validation.

### What didn't work

The first implementation exposed `strategy` in the UI child placement schema, which broke existing tests because the visual graph does not render strategy as a node. I fixed this by filtering the served placement schema to node kinds the UI actually renders.

### What I learned

Root `STRATEGY.md` and top-level `strategies/<slug>/STRATEGY.md` can coexist cleanly if validation treats both as strategy period sources and then checks overlap across the combined set.

### What was tricky

`STRATEGY.md` is both a root prose document today and a future graph node type. The implementation needed to support the future top-level collection without forcing the UI to immediately present strategy as a graph node.

### What warrants review

Review `/src/outcome_engineering/graph.py` for the strategy period validation rules, `/tests/test_graph.py` for the regression coverage, and `/product/STRATEGY.md` for whether the chosen date period matches the intended current strategic window.

### Future work

The visual editor could later show the active strategy period explicitly and offer an archive/history view for older strategies. `oe new strategy` could also accept `--starts` and `--ends` options to avoid placeholder dates.
