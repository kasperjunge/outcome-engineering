# Diary: Assumption tests as a unified concept

This removes opportunity-level assumptions and replaces the separate `assumption` and `experiment` node kinds with a single `assumption-test` kind, aligning the framework with Continuous Discovery Habits.

## Step 1: Unify assumptions and experiments into assumption tests

**Author:** main

### Prompt Context

**Verbatim prompt:** "I just added support for assumptions on opportunity nodes. Remove that. And also, I just discovered that Continuous Discovery Habits do not describe experiments. They are just using the concept 'Assumption Tests' as a unified concept for Assumptions and Experiments. Please implement that in the oe framework aswell."
**Interpretation:** Revert the opportunity-level assumptions change, then collapse the `assumption` and `experiment` node kinds into one `assumption-test` kind that lives under solutions.
**Inferred intent:** Match the framework's discovery vocabulary and structure to Continuous Discovery Habits, where a solution's assumptions and the tests of those assumptions are a single concept.

### What I did

I removed assumptions as a valid child of opportunities in `/src/outcome_engineering/model.py` (`PARENT_KIND_TO_CHILD_KIND` and `ALLOWED_CHILD_RELATIONSHIPS`).

I replaced the `assumption` and `experiment` kinds with a single `assumption-test` kind across the model: marker file `ASSUMPTION_TEST.md`, relationship directory `assumption-tests/`, and parent rule solution → assumption-test. I simplified `RELATIONSHIP_ORDER` to `outcomes, opportunities, solutions, assumption-tests, prds`.

In `/src/outcome_engineering/graph.py` I merged the old `assumption` and `experiment` templates into one `assumption-test` template (Assumption, Risk Type, Test, Success / Failure Signal, Decision It Informs) and removed the now-redundant experiment-parent validation special case.

I pointed `/src/outcome_engineering/example.py` at `KIND_TO_MARKER_FILE` instead of deriving the marker from `kind.upper()`, so a hyphenated kind still maps to the `ASSUMPTION_TEST.md` marker without drift. I rebuilt the example graph: dropped the opportunity-level assumption and folded each solution's assumption plus its experiment into a single assumption test.

I updated `/tests/test_graph.py`, the bundled `oe-cli` skill in both `/skills/oe-cli/SKILL.md` and `/src/outcome_engineering/skills/oe-cli/SKILL.md`, and the vocabulary in `/product/VISION.md`.

### Why

Continuous Discovery Habits models the opportunity solution tree as outcome → opportunities → solutions → assumption tests, with no separate experiment artifact. Collapsing the two kinds removes a layer the method does not use and keeps assumptions where they belong: under the solution whose risk they describe.

### What worked

The model centralizes parent-child rules and relationship ordering, so create, validate, discover, trace, context, tree, and the `new` command all picked up the new kind without command-specific edits. `uv run pytest`, `uv run oe create-example --force`, `uv run oe validate`, and `uv run oe tree` all passed.

### What didn't work

No command failed.

### What I learned

Routing the example generator through `KIND_TO_MARKER_FILE` removed a latent inconsistency: a two-word kind would otherwise have produced `ASSUMPTION-TEST.md` from `kind.upper()` while the model expected `ASSUMPTION_TEST.md`.

### What was tricky

The bundled `oe-cli` skill still exists in two copies that must stay byte-identical until packaging has a single source of truth, so both were updated together.

### What warrants review

Review `/src/outcome_engineering/model.py` and `/src/outcome_engineering/graph.py` for whether the assumption-test template and the solution → assumption-test rule match the intended discovery model. Validate with `uv run pytest`, `uv run oe create-example --force`, and `uv run oe validate`.

### Future work

The `challenge-assumptions` skill still speaks of assumptions, which remains correct since an assumption test tests an assumption. If the framework later wants assumption-test status or risk-category fields, extend the template deliberately rather than reintroducing separate kinds.
