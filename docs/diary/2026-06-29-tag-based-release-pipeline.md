# Diary: Tag-based release pipeline

Added a GitHub tag-triggered release pipeline for the Outcome Engineering package and bundled an `oe-release` skill so agents have a repeatable release procedure.

## Step 1: Add release automation and release skill

**Author:** main

### Prompt Context

**Verbatim prompt:** please to that
**Interpretation:** The user approved the proposed plan to add a simple GitHub tag-based release pipeline inspired by `agr`, plus a bundled `oe-release` skill.
**Inferred intent:** Make releases repeatable and agent-operable: prepare versions and changelog entries locally, push a `vX.Y.Z` tag, let GitHub Actions publish to PyPI, and create a GitHub Release.

### What I did

I added `/.github/workflows/test.yml` for PR and `main` branch checks, and `/.github/workflows/publish.yml` for tag-triggered publish automation. The publish workflow runs tests, builds with `uv build`, verifies that a pushed tag matches `/pyproject.toml`, publishes through PyPI trusted publishing, and creates a GitHub Release from `/CHANGELOG.md`.

I added `/CHANGELOG.md` with an `[Unreleased]` section and an initial `0.1.0` entry. I added identical `oe-release` skill copies at `/skills/oe-release/SKILL.md` and `/src/outcome_engineering/skills/oe-release/SKILL.md`. I updated `/src/outcome_engineering/skill_installer.py` so `oe-release` is part of the bundled skill set installed by the existing installer functions.

I validated both skill copies with `uvx --with pyyaml python /Users/kasperjunge/.codex/skills/.system/skill-creator/scripts/quick_validate.py ...`, confirmed they match with `cmp -s`, ran `uv run pytest`, ran `uv run oe validate product`, built the package with `uv build`, and inspected the built wheel to confirm it includes `outcome_engineering/skills/oe-release/SKILL.md`.

### Why

The release should be driven by immutable git tags rather than a manual local publish step. Keeping the release process in a skill makes the package self-documenting for agent-assisted maintenance, and adding the skill to the bundled installer ensures users can install it alongside the existing Outcome Engineering skills.

### What worked

The existing installer tests already assert against `SKILL_NAMES`, so adding `oe-release` to that tuple exercised the new bundled skill without new bespoke tests. The `uv_build` package build included the new source skill file automatically. Local tests passed: `47 passed in 1.80s`.

### What didn't work

Running `python /Users/kasperjunge/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/oe-release` failed because this shell has no `python` binary: `zsh:1: command not found: python`.

Running the validation script with `uv run python` then failed because the project environment does not include PyYAML: `ModuleNotFoundError: No module named 'yaml'`.

Running two parallel `uvx --with pyyaml ... quick_validate.py` commands caused a uv cache race for one process: `error: failed to rename file from /Users/kasperjunge/.cache/uv/builds-v0/.tmpjozzFe to /Users/kasperjunge/.cache/uv/archive-v0/WhbINXS2G0Pgdrhf: Directory not empty (os error 66)`. Rerunning the second validation serially succeeded.

### What I learned

This repo intentionally keeps dev dependencies minimal, so external skill validation should use an isolated `uvx --with pyyaml` invocation rather than adding PyYAML to `/pyproject.toml`. The `agr` workflow was a useful reference, but its manual `workflow_dispatch` pattern would compare the package version to a branch name on non-tag runs; the Outcome Engineering workflow avoids that by limiting tag verification, publishing, and GitHub Release creation to tag pushes.

### What was tricky

The working tree already had unrelated product graph and skill changes before this task started. I kept the release work scoped to new workflow files, changelog, the new release skill, and the installer tuple so those existing changes were not reverted or overwritten.

### What warrants review

Review `/.github/workflows/publish.yml` for repository policy fit, especially the PyPI environment name and trusted publishing assumptions. Review both `oe-release` skill copies for process language and make sure the required release checks match how maintainers want to cut versions.

### Future work

Configure PyPI trusted publishing for the GitHub repository and the `outcome-engineering` project before pushing the first real release tag.

## Step 2: Add linting and type checks

**Author:** main

### Prompt Context

**Verbatim prompt:** please also make sure that the project is tested using ruff and ty
**Interpretation:** The user wants the project checks and release pipeline to include Ruff and ty, not only pytest and package build validation.
**Inferred intent:** Make quality gates catch lint, formatting, and typing issues before merge and before publishing a release.

### What I did

I added `ruff` and `ty` to the `/pyproject.toml` dev dependency group with `uv add --dev ruff ty`, which also updated `/uv.lock`. I updated `/.github/workflows/test.yml` and `/.github/workflows/publish.yml` so both CI paths run `uv run ruff check .` and `uv run ty check` before `uv run pytest`. I updated both `oe-release` skill copies at `/skills/oe-release/SKILL.md` and `/src/outcome_engineering/skills/oe-release/SKILL.md` so local release checks and pipeline-stage descriptions include Ruff and ty.

### Why

Putting Ruff and ty in both dev dependencies and workflows keeps local release preparation aligned with GitHub Actions. Adding the same commands to `oe-release` prevents future release agents from cutting tags without running the full quality gate.

### What worked

`uv add --dev ruff ty` resolved and installed the tools cleanly, adding `ruff==0.15.20` and `ty==0.0.55` to the lockfile.

### What didn't work

No failure occurred during this step.

### What I learned

The release workflow had a single `quality` job, so adding lint, format, and type checks there keeps publishing blocked by all quality gates without changing downstream build, publish, or release jobs.

### What was tricky

The two `oe-release` skill copies need to remain identical, so the same procedural updates had to be applied to both files.

### What warrants review

Review whether `ruff format --check .` should be enforced later in a separate formatting commit. The current CI gate uses `ruff check .` to avoid broad formatting churn in this release-pipeline change.

### Future work

If type checking is too strict or too loose, add explicit ty configuration in `/pyproject.toml` instead of relying only on defaults.
