# Diary: Playwright-style skill install

Adjusted the skill install UX to mirror Playwright CLI's `install --skills` pattern.

## Step 1: Add install --skills

**Author:** main

### Prompt Context

**Verbatim prompt:** have you checked the playwright-cli way of installing skill i want that
**Interpretation:** The existing `oe install-skill` command was too custom. The user wants the Playwright-style CLI UX where skills are installed through an `install --skills` subcommand.
**Inferred intent:** Make `outcome-engineering` feel familiar to agents and humans who have seen Playwright CLI's skill installation flow.

### What I did

I added `oe install --skills`, which installs the bundled `oe-cli` skill into `.claude/skills/oe-cli` in the current project. I also added `oe install --skills=agents`, which installs into `.agents/skills/oe-cli`. The existing `oe install-skill` command remains as a compatibility/cross-tool command with `--agent codex`, `--agent claude`, `--agent all`, and `--target`.

### Why

Project-local skill installation is a better default for this package because the product graph lives in a repository and the relevant agent instructions should be easy to install beside that repo.

### What worked

From a temporary project directory, `uv run --project <repo> oe install --skills --force` created `.claude/skills/oe-cli/SKILL.md`, and `uv run --project <repo> oe install --skills=agents --force` created `.agents/skills/oe-cli/SKILL.md`.

### What didn't work

Typer does not naturally expose an optional-value flag like `--skills` / `--skills=agents` in the generated help. I used permissive argument parsing for the `install` command so the exact Playwright-style syntax works.

### What I learned

The install UX now has two layers: `oe install --skills` for project-local Playwright-style installation, and `oe install-skill` for explicit global/cross-tool installation.

### What was tricky

Matching the exact optional-argument UX required parsing `ctx.args` rather than a normal Typer option.

### What warrants review

Review whether `oe install-skill` should eventually be deprecated once `oe install --skills` is stable enough.

### Future work

Improve help output for `oe install` so `--skills` is visible despite the custom parsing.

