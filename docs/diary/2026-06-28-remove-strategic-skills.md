# Diary: Remove strategic skills

This records the cleanup after deciding that Outcome Engineering should only ship the `oe-cli` skill for now.

## Step 1: Keep only oe-cli

**Author:** main

### Prompt Context

**Verbatim prompt:** "Great. I also want to remove the other skills that is not the oe-cli because i've decided to change the strategy"
**Interpretation:** Remove the bundled non-`oe-cli` agent skills from the source tree, package resources, local skill dependency manifest, and public docs.
**Inferred intent:** Reset the agent-skill strategy so the CLI skill remains the single supported operating manual while the broader product strategy changes.

### What I did

I deleted `/skills/challenge-assumptions/SKILL.md`, `/skills/challenge-product-intent/SKILL.md`, `/skills/craft-vision-strategy/SKILL.md`, and their packaged copies under `/src/outcome_engineering/skills/`. I reduced `/src/outcome_engineering/skill_installer.py` so `SKILL_NAMES` only contains `oe-cli`, and updated `/src/outcome_engineering/cli.py` help text from plural "skills" to singular "skill".

I removed the three local skill dependencies from `/agr.toml` with `agr remove ./skills/challenge-assumptions ./skills/challenge-product-intent ./skills/craft-vision-strategy`, which also regenerated `/agr.lock`. I removed `/docs/agent-entry-points.md` and the README link to it because that doc described the deleted skills. I refreshed the active installed project copy with `uv run oe install-skill --target .agents/skills/oe-cli --force`.

### Why

The old strategic skills encoded a strategy the user no longer wants to ship. Keeping them in the install bundle, agr manifest, or README would make the repository advertise a product direction that is no longer current.

### What worked

`agr remove` cleanly updated both `/agr.toml` and `/agr.lock`, which avoided hand-editing the generated lockfile. The existing installer tests were already written against `SKILL_NAMES`, so reducing that tuple made the tests assert the new one-skill bundle without extensive rewrites.

### What didn't work

No command failed during this step. `rg` found many historical diary references to the removed skills, but those were intentionally left alone as history rather than rewritten.

### What I learned

The live skill surface is controlled in three places: root source skills under `/skills`, packaged resources under `/src/outcome_engineering/skills`, and agr dependencies in `/agr.toml`. Removing a skill properly means addressing all three.

### What was tricky

The local `.agents/skills` directory contains generated installed skills and also the external `agr-cli` skill. The cleanup needed to remove the obsolete Outcome Engineering skill directories without disturbing the unrelated `agr-cli` install.

### What warrants review

Review `/src/outcome_engineering/skill_installer.py`, `/agr.toml`, and the deleted skill directories to confirm `oe-cli` is now the only bundled Outcome Engineering skill. Validate with `uv run pytest`, `uv run oe validate product`, and `agr sync --locked`.

### Future work

`/product/STRATEGY.md` still describes the older strategy with the three agent entry points. It should be rewritten when the new strategy is ready to capture in the product graph.
