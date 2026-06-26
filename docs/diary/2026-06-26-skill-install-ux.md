# Diary: Skill install UX

Added CLI support for installing the bundled `oe-cli` skill across agent tools.

## Step 1: Add install-skill command

**Author:** main

### Prompt Context

**Verbatim prompt:** That's actually an approach I like: package outcome engineering framework, outcome engineering, and the package is outcome engineering - outcome engineering and then the command is OE. I like that.

Do we have a skill for the CLI tool? Have we made that? If we have, I want to make it in a dir called skills in the root repo and it should just be named OE-CLI. Explain it in a way that is sensible for the agent on how to use this tool.

Other than that I would like to be able to install that skill the same way the plot play right CLI is installing a skill. I think it's playwright here, live that she lied--skills or something like that. Please check it out. I want to have the same UX in this package
**Interpretation:** Keep the package name as `outcome-engineering`, keep the CLI command as `oe`, rename the bundled skill to `oe-cli`, and add a CLI install command for installing the skill into agent tool skill directories.
**Inferred intent:** Make the package self-contained: installable with uv/uvx and able to install its own agent skill with a familiar CLI subcommand.

### What I did

I renamed the repo-local skill to `/skills/oe-cli/SKILL.md` and added a packaged copy at `/src/outcome_engineering/skills/oe-cli/SKILL.md`.

I added `/src/outcome_engineering/skill_installer.py` and the `oe install-skill` command. It supports `--agent codex`, `--agent claude`, `--agent all`, and `--target` for custom tool directories.

### Why

Agents need instructions for when to use `oe`, and users should be able to install that skill from the same package that provides the CLI.

### What worked

`uv run pytest` passed. `oe install-skill --agent all` installed the skill into both Codex and Claude target directories when `CODEX_HOME` and `CLAUDE_HOME` were set. `oe install-skill --target` also worked. The built wheel includes the packaged skill file.

### What didn't work

The first naming pass used uppercase `OE-CLI`, but the requested skill name should be lowercase. I renamed it to `oe-cli` throughout the repo and package.

### What I learned

The package can ship the skill as importlib resources under `outcome_engineering/skills/oe-cli`, which keeps the install command independent of the source checkout layout.

### What was tricky

Different agent tools use different home directories. The first supported targets are Codex and Claude, with `--target` available for other tools until their conventions are confirmed.

### What warrants review

Review `/skills/oe-cli/SKILL.md` to confirm the usage guidance is sufficiently clear for agents and not too Codex-specific.

### Future work

Add more first-class `--agent` targets when their skill directory conventions are known.

