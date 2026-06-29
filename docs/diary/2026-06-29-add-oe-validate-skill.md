# Diary: Add OE Validate Skill

Add `oe-validate` as a bundled Outcome Engineering skill so users can install it with the CLI skill installer.

## Step 1: Ship OE Validate With Bundled Skills

**Author:** main

### Prompt Context

**Verbatim prompt:** ohh, the oe-validate is for the outcome-engineering repo, not the agent-central or clt repo. the agent-central app in the clt repo should just use it as a dev dep (even thought agr does not support that, so just make it a normal dep in agr). the oe-validate is supposed to be shipped witht he cli when running the --skills thing.
**Interpretation:** Move `oe-validate` into the Outcome Engineering repository and include it in the bundled skill installer.
**Inferred intent:** Make `oe-validate` part of the OE package distribution rather than a CLT-local skill.

### What I did

I created `/skills/oe-validate/SKILL.md` and the matching packaged copy at `/src/outcome_engineering/skills/oe-validate/SKILL.md`. I added `oe-validate` to `SKILL_NAMES` in `/src/outcome_engineering/skill_installer.py` so `oe install --skills`, `oe install --skills=agents`, and `oe install-skill --agent all` install it with the other bundled skills. I registered the root skill in `/agr.toml` with `agr add ./skills/oe-validate`, which refreshed `/agr.lock`.

### Why

`oe-validate` describes how to update the OE CLI, run deterministic validation, and propose fixes for validation failures. That workflow belongs with the package that owns the CLI and graph schema.

### What worked

The root and packaged skill copies match. `uvx --with pyyaml python /Users/kasperjunge/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/oe-validate` returned `Skill is valid!`. `uv run pytest tests/test_graph.py -q` passed with `47 passed`. `uv build` produced a wheel containing `outcome_engineering/skills/oe-validate/SKILL.md`.

### What didn't work

Nothing failed in this repo. In the CLT repo, adding `kasperjunge/outcome-engineering/oe-validate` as an AGR dependency failed because the new skill is not on the Outcome Engineering default branch yet.

### What I learned

The installer tests already cover bundled skill installation through `SKILL_NAMES`, so adding the new name exercises the `--skills` install path without bespoke test code.

### What was tricky

The same skill must exist in two source locations until the package has a single generated source of truth for root and packaged skills.

### What warrants review

Review both `oe-validate` skill copies for concision and the approval boundary before graph edits.

### Future work

After this branch lands, add `oe-validate` as a normal AGR dependency in downstream repos that should consume the packaged skill.
