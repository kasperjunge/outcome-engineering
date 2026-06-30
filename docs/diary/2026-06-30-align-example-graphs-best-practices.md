# Diary: Align example graphs with OE Best Practices

Brief description of the goal and context for this task.

The task was to apply the repo-local OE Best Practices skill to the example product graphs under `/examples/boligsiden` and `/examples/star` so their content better separates vision, strategy, outcomes, opportunities, solutions, assumption tests, and PRDs.

## Step 1: Apply OE Best Practices to example graphs

**Author:** main

### Prompt Context

**Verbatim prompt:** Hello. Please in the Outcome Engineering repo apply the OE Best Practices skill to the example graphs so they align with that. You don't have to ask me any questions, just do it. Tell me what you've done after that
**Interpretation:** Update the example product graphs in the Outcome Engineering repo using the repo-local `oe-best-practices` skill, without asking clarification questions.
**Inferred intent:** Make the example graphs better demonstrations of semantically clean Outcome Engineering graph content.

### What I did

I created a worktree branch with `git worktree add .worktrees/apply-oe-best-practices-examples -b apply-oe-best-practices-examples` before editing. I read `/src/outcome_engineering/skills/oe-best-practices/SKILL.md` and all of its relevant reference files for vision, strategy, ICPs, outcomes, opportunities, solutions, assumption tests, and PRDs. I validated both example graphs before editing with `uv run oe validate examples/boligsiden` and `uv run oe validate examples/star`.

I updated `/examples/boligsiden` and `/examples/star` content only. The changes clarify durable vision language, make strategy state the current bet and what is not being chosen, tune outcomes toward changed user behavior and mixed measures, remove solution leakage from several opportunities, add explicit mechanism sections to solution nodes, add product-intent trace and unknowns to PRDs, and localize mixed English labels in Danish STAR content.

I validated both graphs again with `uv run oe validate examples/boligsiden && uv run oe validate examples/star`.

### Why

The best-practices references treat each node type as a contract. The example graphs were structurally valid, but some nodes were too terse or mixed layers: strategies did not fully state the wedge and logic of advantage, solutions did not always explain why the intervention should work, PRDs lacked explicit trace and unknowns, and STAR had mixed English/Danish labels.

### What worked

The repo-local skill was concise and mapped cleanly to the graph files. The CLI validation confirmed the graph structure stayed valid before and after the content edits.

### What didn't work

My first `apply_patch` attempt used paths relative to `/Users/kasperjunge/Agent` instead of the worktree and failed before changing files:

```text
apply_patch verification failed: Failed to read file to update /Users/kasperjunge/Agent/examples/boligsiden/VISION.md: No such file or directory (os error 2)
```

I reapplied the patch using paths rooted at `/Code/kasperjunge/private/outcome-engineering/.worktrees/apply-oe-best-practices-examples/...`, and the edits landed cleanly.

### What I learned

The example graphs were already valid product graphs, so the work was mostly semantic rather than structural. The largest repeatable gap was PRD trace: adding product intent and unknowns makes the PRDs better examples without prescribing implementation details.

### What was tricky

The Danish STAR graph needed content alignment without changing its domain vocabulary or translating the whole graph. I kept the changes narrow: localized labels, added rationale sections, and preserved existing Danish content shape.

### What warrants review

Review `/examples/boligsiden/STRATEGY.md`, `/examples/star/STRATEGY.md`, the solution `Why This Could Work` / `Hvorfor Det Kan Virke` sections, and the new PRD `Product Intent` / `Produktintention` plus unknowns sections. Validate with:

```sh
uv run oe validate examples/boligsiden
uv run oe validate examples/star
```

### Future work

The Boligsiden assumption tests still use compact `Success:` / `Failure:` phrasing. They are valid and state evidence in advance, but they could be reformatted later to match the clearer confidence-up/confidence-down style used in the STAR cleanup.
