# Outcome Engineering

Outcome Engineering is a Python CLI for maintaining repo-native product graphs. The `oe` command validates, inspects, serves, and edits a filesystem graph rooted at `product/`, where product intent is captured as vision, strategy, ICPs, outcomes, opportunities, solutions, assumption tests, and PRDs.

Use `uv run oe --help` to inspect the current CLI. Use `uv run oe validate product` before and after graph structure changes, and prefer `uv run oe new ...` over hand-creating graph directories.

The `oe-cli` skill is the agent-facing operating manual for this CLI. Whenever the CLI command surface, graph model, or recommended workflow changes, update `src/outcome_engineering/skills/oe-cli/SKILL.md`.

The skill should always stay in sync with the actual CLI, especially commands and options shown by `uv run oe --help`.
