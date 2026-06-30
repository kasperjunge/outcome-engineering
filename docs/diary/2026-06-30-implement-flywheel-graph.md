# Diary: implement flywheel graph

This records the first implementation pass for the experimental flywheel graph MVP.

## Step 1: Implement flywheel artifact, context, and UI

**Author:** main

### Prompt Context

**Verbatim prompt:** I'm working on outcome engineering. Please implement the PRD on the flywheel feature or please make a plan for at least four implementing
**Interpretation:** Implement the existing flywheel PRD if feasible, otherwise produce an implementation plan.
**Inferred intent:** Turn the experimental flywheel graph PRD into a working repo-native feature while preserving the normal product graph model.

### What I did

I created a worktree at `/.worktrees/implement-flywheel-graph` and implemented the flywheel as a separate artifact under `/product/flywheels/strategy/`, not as a normal product graph node. I added flywheel dataclasses and constants in `/src/outcome_engineering/model.py`, parsing and structural validation in `/src/outcome_engineering/graph.py`, flywheel context output in `/src/outcome_engineering/cli.py`, payload serialization in `/src/outcome_engineering/serve.py`, and a separate Flywheel UI mode in `/src/outcome_engineering/templates/graph.html`.

I added a dogfood flywheel at `/product/flywheels/strategy/FLYWHEEL.md` with four flywheel nodes under `/product/flywheels/strategy/nodes/`. I added tests in `/tests/test_graph.py` for validation, discovery, context, server payload, and template hooks.

Validation commands run:

```sh
uv run oe validate product
uv run pytest
uv run oe context prd.experimental-flywheel-graph-mvp --root product | rg -n "Flywheel Context|flywheel.strategy|flywheel-node"
curl -s http://127.0.0.1:8765/api/graph | jq '.flywheel.id, (.flywheel.nodes | length)'
```

I also ran Playwright CLI against `http://127.0.0.1:8765/` and verified that the Flywheel button appears, flywheel mode renders four nodes and four directed edges, and selecting an edge shows its causal explanation in the detail panel.

### Why

The PRD says the flywheel should be optional, strategy-level, visually inspectable, agent-legible, and separate from the normal outcome -> opportunity -> solution trace graph. Keeping it as a dedicated artifact reader and UI mode preserves that boundary while making it available to validation, context, and the graph UI.

### What worked

The existing frontmatter parser and server payload pattern were enough to support the artifact without introducing a new dependency. The existing SVG node renderer could be reused for flywheel nodes after adding a custom click handler, which kept the visual design consistent while preventing flywheel nodes from inheriting normal graph edit/delete behavior.

### What didn't work

My first large `apply_patch` against `/src/outcome_engineering/graph.py` failed because the expected context around `title_from_slug` did not match:

```text
apply_patch verification failed: Failed to find expected lines in /Users/kasperjunge/Agent/Code/kasperjunge/private/outcome-engineering/.worktrees/implement-flywheel-graph/src/outcome_engineering/graph.py:
def title_from_slug(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.replace("_", "-").split("-") if part)
```

I split the parser changes into smaller patches and continued.

The plain `python` command was not available:

```text
zsh:1: command not found: python
```

I used `uv run python -m py_compile ...` instead.

My first Playwright CLI eval calls placed `--raw` before the command and failed with:

```text
Unknown command: JSON.stringify([...document.querySelectorAll('button')].map(b => ({id:b.id,text:b.textContent,display:getComputedStyle(b).display,disabled:b.disabled})))
```

I retried with `playwright-cli eval "..."`, which worked.

### What I learned

The current validator ignores unknown marker files unless explicitly taught about them, which made it possible to add flywheel validation alongside the normal graph without polluting `MARKER_FILES` or the product node discovery path.

### What was tricky

The important modeling constraint was to make flywheels validate structurally without becoming trace-chain nodes. The UI had a similar constraint: the flywheel needed reusable graph rendering, but not normal node CRUD actions because those endpoints only understand product graph nodes.

### What warrants review

Review `/src/outcome_engineering/graph.py` for whether the single-flywheel validation rule is strict enough and whether the causal explanation check should require a specific `## Why this creates the next step` section rather than any non-heading body text. Review `/src/outcome_engineering/templates/graph.html` for whether the separate Flywheel mode is the right first UI entry point.

### Future work

Add first-class editing or creation commands for flywheel artifacts if direct markdown editing proves too rough. Agent critique should probably remain in skills/prompts until dogfooding shows which critique workflow is useful.

