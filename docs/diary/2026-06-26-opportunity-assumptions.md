# Diary: Opportunity-level assumptions

This task changed the product graph so assumptions can optionally live under opportunities as well as solutions, while experiments remain children of assumptions.

## Step 1: Allow assumptions under opportunities

**Author:** main

### Prompt Context

**Verbatim prompt:** /var/folders/k2/7mt08_g54qqbhhdwsntm1z780000gn/T/tmp.qN3lDRr6Vq/outcome-engineering-assumptions-handoff.md
**Interpretation:** Continue the handed-off product model discussion and implement the agreed graph structure once clarified.
**Inferred intent:** The product graph should represent opportunity-level uncertainty before solution selection, without making assumptions required.

### What I did

I created the `/.worktrees/opportunity-assumptions` worktree from the repository root before editing. I updated `/src/outcome_engineering/model.py` so opportunities may have `assumptions/` as well as `opportunities/` and `solutions/`. I added `RELATIONSHIP_ORDER` and used it from `/src/outcome_engineering/graph.py` so opportunity children render as opportunities, assumptions, then solutions.

I updated `/tests/test_graph.py` to cover creating an assumption under an opportunity, creating an experiment under that assumption, and preserving the agreed child ordering. I updated `/src/outcome_engineering/example.py` and regenerated `/examples/delegation-product-graph` so the example includes `opportunity.users-do-not-know-what-to-delegate/assumptions/delegation-pain-is-frequent/experiments/frequency-interviews`.

I updated `/README.md`, `/docs/graph.md`, `/docs/example-structure.md`, `/docs/glossary.md`, `/skills/oe-cli/SKILL.md`, and `/src/outcome_engineering/skills/oe-cli/SKILL.md` so humans and bundled agent instructions describe assumptions as valid under opportunities or solutions.

### Why

Generated or discovered opportunities can be plausible but not real. Allowing optional opportunity-level assumptions gives teams a first-class place to test whether an opportunity exists before selecting a solution. Keeping experiments under assumptions preserves the existing learning model.

### What worked

The current graph code already centralizes parent-child rules, so the behavioral change was small. `create_node`, validation, discovery, trace, context, and tree all picked up the new parent rule from the model.

### What didn't work

No command failed. The commands run were `uv run oe create-example --force`, `uv run pytest`, `uv run oe validate examples/delegation-product-graph`, and `uv run oe tree examples/delegation-product-graph`.

### What I learned

Tree ordering had been implicit through alphabetical relationship directory sorting. Adding `assumptions/` under opportunities made that visible because alphabetical order would have shown assumptions before sub-opportunities.

### What was tricky

There are two copies of the bundled `oe-cli` skill, one in `/skills/oe-cli/SKILL.md` and one in `/src/outcome_engineering/skills/oe-cli/SKILL.md`. Both need to stay aligned until the packaging setup has a single source of truth.

### What warrants review

Review `/src/outcome_engineering/model.py` and `/src/outcome_engineering/graph.py` for whether the allowed parent-child rules and child display order match the intended product model. Validate with `uv run pytest`, `uv run oe validate examples/delegation-product-graph`, and `uv run oe tree examples/delegation-product-graph`.

### Future work

If assumptions later need to attach to outcomes, strategy, or vision, extend the same parent-child rule table deliberately rather than introducing a separate assumption type.
