# Diary: Strategic agent skills

This captures the first concise skills for the three strategic Outcome Engineering entry points.

## Step 1: Add strategic skills and plural installation

**Author:** main

### Prompt Context

**Verbatim prompt:** "let's make the simplest version of the skills we need to drive the strategic bets. keep em concise, let the agent and the graph do its work. i guess they should also use the oe-cli skill and the oe cli of course"
**Interpretation:** Create small agent skills for the strategic bets and make sure they rely on the existing `oe-cli` skill and `oe` CLI instead of duplicating graph mechanics.
**Inferred intent:** Turn the strategy into usable agent entry points that can be installed with the package and guide agents toward graph-backed product work.

### What I did

I added `/skills/challenge-assumptions/SKILL.md`, `/skills/craft-vision-strategy/SKILL.md`, and `/skills/challenge-product-intent/SKILL.md`, plus packaged copies under `/src/outcome_engineering/skills/`. Each skill is concise and instructs agents to use `oe-cli`, inspect or validate the graph, keep outputs short, and propose graph changes for human approval.

I updated `/src/outcome_engineering/skill_installer.py` so the normal install paths can install all bundled skills: `oe-cli`, `challenge-assumptions`, `craft-vision-strategy`, and `challenge-product-intent`. I kept the exact-target `install_skill()` path as the single `oe-cli` install for compatibility.

I updated `/src/outcome_engineering/cli.py` so `oe install --skills` and `oe install-skill --agent ...` install all bundled skills by default. I updated tests in `/tests/test_graph.py` and adjusted README/docs copy from singular "skill" to plural "skills".

### Why

The new product strategy depends on three agent-native entry points: challenge assumptions, craft vision and strategy, and challenge product intent. Shipping them as skills makes those jobs discoverable and repeatable while the product graph remains the durable memory.

### What worked

`uv run pytest` passed with 14 tests. `uv run oe validate product` passed. A direct install smoke test from a temporary project installed all four skills into `.claude/skills`.

### What didn't work

My first smoke-test command used the wrong option shape:

```sh
tmpdir=$(mktemp -d) && uv run oe install --skills --force --project "$tmpdir" 2>/dev/null || true
```

It returned:

```text
unknown install option: --project
```

The correct consumer-style smoke test was:

```sh
tmpdir=$(mktemp -d) && cd "$tmpdir" && uv run --project /Users/kasperjunge/Agent/Code/kasperjunge/private/outcome-engineering/.worktrees/strategic-skills oe install --skills --force && find .claude/skills -maxdepth 2 -name SKILL.md -print | sort
```

That installed all four skill directories.

### What I learned

The skills can stay small if they defer graph operations to `oe-cli` and keep the product judgment boundary explicit: `oe` validates structure, while humans approve product truth.

### What was tricky

The installer had been designed around a single bundled skill. The safest path was adding plural install helpers for normal installs while preserving the existing single-skill helper behavior for exact-target installs and compatibility.

### What warrants review

Review the three new skill descriptions for trigger strength and clarity. Review the installer behavior to confirm `install-skill --target` should remain single-skill rather than installing a bundle into a target root.

### Future work

The next likely step is to run real prompts through the skills and tighten them based on whether agents ask better questions, inspect the graph reliably, and propose useful graph edits without overproducing.
