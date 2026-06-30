# Diary: Decouple OE skills

This records the refactor that removed duplicated shipped skill sources, made `oe-release` repo-local, and clarified the responsibilities between the Outcome Engineering skills.

## Step 1: Split shipped skills from repo-local skills

**Author:** main

### Prompt Context

**Verbatim prompt:** "Okay regarding the duplication, I would like us to actually find some way to avoid this. This duplication only happened in one place and also the OEE release is not a skill that should be shipped with the package. That is a skill that is needed for the repo to automate the release process of it so that is unrelated to the shipped package.
I suspected that the OEE skill and the graph audit and the OEE best practices had some overlap so how can we actually decouple these? I would really like to decouple these. I want to use the OEE best practices for the cutting-edge and the recommended thinking on how to actually write the content of each note.
Please help me think through some solutions here. Also if we maybe need, I guess, these skills can actually depend on each other. We can assume that people are using them together so maybe we could do something where the best practices are actually stored in that skill and then there is an action-based command for actually auditing an existing graph.
Thoughts on that? I think the OEE skill should not repeat the OECLI stuff. It should also just reference the cli skill and then it should use the best practices for its thinking and comparing its thinking about actually how to do it and comparing it to the existing graph. I think it should just relentlessly ask questions. I think that was what I intended with it.
Next one: I think the OEE validate should not upgrade the actual OEE package. It should just run validate and then catch whatever is wrong with it and then fix it. It is basically just the validate command wrapped in a skill for self-healing and making the UX of actually fixing stuff easier.
For the OEE best practices, please link to all of the concepts described in the references. The dogfooding ones in the agent skills and the close girls should just be installed in this repository. Of course the agent and codecs and close skill folder should be getting north but please add them using a gr so we make sure that they're installed in this repo. Or should they be installed in this repo or should they be installed in the agent workspace? I'm not actually sure.
Now reading your best improvement path, okay, just some comments on your best improvement paths:
- sync test for skills versus source outcome engineering skills. Maybe I would just prefer to actually have some routine to actually just have them in one place.
- I actually forgot the ICP best practices guidance, where to start"

**Interpretation:** Remove the duplicated root and packaged shipped skill copies, keep `oe-release` available only as a repo-local maintenance skill, decouple skill responsibilities, add ICP best-practices guidance, and use agr to install the dogfooding skills locally.

**Inferred intent:** The skill set should have a single source of truth, clearer boundaries, and repo-local dogfooding without leaking maintainer-only release automation into the package.

### What I did

I created the `/.worktrees/decouple-oe-skills` worktree on branch `decouple-oe-skills` before editing. I made `/src/outcome_engineering/skills/` the only tracked source for package-shipped skills and deleted the duplicate root copies for `oe-cli`, `oe-grill`, `oe-graph-audit`, `oe-validate`, and `oe-best-practices`. I left `/skills/oe-release/SKILL.md` in root as a repo-local skill and deleted `/src/outcome_engineering/skills/oe-release/SKILL.md` so it is no longer packaged or installed by the package installer.

I removed `oe-release` from `SKILL_NAMES` in `/src/outcome_engineering/skill_installer.py`. I updated `/agr.toml` so agr dogfooding installs the canonical shipped skill paths from `/src/outcome_engineering/skills/`, plus the repo-local `/skills/oe-release`. I ran `agr sync`, which refreshed `.agents/skills` and `.claude/skills`; those directories remain ignored by git.

I slimmed `/src/outcome_engineering/skills/oe-cli/SKILL.md` so it owns CLI and graph-structure mechanics, not product judgment. I updated `/src/outcome_engineering/skills/oe-graph-audit/SKILL.md` to apply `oe-best-practices` instead of duplicating the detailed rules. I updated `/src/outcome_engineering/skills/oe-grill/SKILL.md` so it references `oe-cli` and `oe-best-practices` and focuses on asking focused product questions. I updated `/src/outcome_engineering/skills/oe-validate/SKILL.md` so it only runs validation and helps fix validation failures, without upgrading the package. I added `/src/outcome_engineering/skills/oe-best-practices/references/icps.md` and linked it from `/src/outcome_engineering/skills/oe-best-practices/SKILL.md`.

I updated `/AGENTS.md` to point maintainers at the single bundled `oe-cli` copy, and added an `/CHANGELOG.md` unreleased entry for the refactor.

### Why

Keeping shipped skills in both `/skills` and `/src/outcome_engineering/skills` made every skill edit a two-place maintenance problem. Moving package-shipped skills to one canonical package-resource location preserves wheel installation while removing drift risk. Keeping `oe-release` in root makes it available to this repository through agr without shipping maintainer release automation to package users.

The skill boundary change makes `oe-best-practices` the single source of truth for product content quality, while `oe-graph-audit` becomes the action skill that applies those rules to an existing graph. `oe-cli` remains the structural operating manual, `oe-grill` becomes the conversational questioning loop, and `oe-validate` becomes a self-healing validation wrapper.

### What worked

`agr sync` handled repo-local dogfooding cleanly after `/agr.toml` moved local dependencies to `/src/outcome_engineering/skills`. The package build confirmed that only the intended shipped skills are included in the wheel.

### What didn't work

The first wheel inspection command used `python`, which is not available in this shell:

```sh
rm -rf dist && uv build && python - <<'PY'
...
PY
```

It failed with:

```text
zsh:1: command not found: python
```

I reran the inspection with `uv run python`, which worked.

### What I learned

For this repo, the practical single-source split is package skills under `/src/outcome_engineering/skills` and maintainer-only repo skills under `/skills`. agr can dogfood either path, so local skill installation does not require the root `/skills` directory to be the source for every skill.

### What was tricky

The duplication was tied to packaging: root `skills/` is convenient for repo-local editing, but the wheel needs package resources under `src/outcome_engineering/skills`. Avoiding duplication means accepting that shipped skill source lives inside the package tree, while root `skills/` is reserved for repo-only tools.

### What warrants review

Review `/src/outcome_engineering/skills/oe-grill/SKILL.md` to confirm "relentless product questioner" is the right behavioral strength. Review `/src/outcome_engineering/skills/oe-graph-audit/SKILL.md` to confirm it now defers enough detail to `oe-best-practices`. Review `/src/outcome_engineering/skills/oe-best-practices/references/icps.md` for product-method fit.

Validation commands run:

```sh
uv run oe validate product
agr sync --locked
uv run pytest
uv build
uv run python - <<'PY'
...
PY
uv run ruff check .
uv run ty check
```

The package wheel contained `oe-best-practices`, `oe-cli`, `oe-graph-audit`, `oe-grill`, and `oe-validate`; it did not contain `oe-release`.

### Future work

Consider whether `oe install --skills` should advertise the installed skill names in help output, now that package users receive several coordinated skills rather than only `oe-cli`.
