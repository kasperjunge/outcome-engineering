# Diary: Agent readiness commands

Added read-only agent commands and a repo-local skill for using Outcome Engineering.

## Step 1: Add list, show, context, and skill

**Author:** main

### Prompt Context

**Verbatim prompt:** Okay you have some really great points there. I like the OE list, the OE show, and the OE context. I think we should create an agent skill that will help you actually know how to use this right and have a good description of when to also use it. I agree with the stable root convention, the product directory root directory, and I agree with that. Please add the things we talked about
**Interpretation:** Add the proposed read-only CLI commands, document `product/` as the stable graph root, and create an agent skill that explains when and how to use the `oe` tool.
**Inferred intent:** Make the tool easier for agents to discover, understand, and use correctly during product and implementation work.

### What I did

I added `oe list`, `oe show`, and `oe context`. `list` prints node ids and paths, `show` prints a node's canonical marker file, and `context` prints trace, children, supporting files, ancestor marker content, and the selected node content.

I added `/skills/outcome-engineering/SKILL.md` with usage guidance for agents, including when to use the tool, when to skip it, the default workflow, and the boundary that `oe validate` checks structure rather than product judgment.

I updated `/README.md` and `/docs/example-structure.md` to include the new commands and `product/` root convention.

### Why

Agents need a clear mechanical workflow: inspect the graph, trace relevant nodes, gather deterministic context, create nodes through the CLI, and validate after structural changes.

### What worked

`uv run pytest` passed with seven tests. `oe list`, `oe show`, and `oe context` worked against the example graph.

### What didn't work

The first `oe context` output only listed ancestor paths. I expanded it to include ancestor marker content because that is more useful for an agent trying to preserve product intent.

### What I learned

`oe context` is the natural bridge between deterministic graph mechanics and future agent-assisted product critique. It should remain deterministic, but provide enough context for a model to reason well.

### What was tricky

The skill should not imply that `oe` makes product judgments. It needs to tell agents that the CLI manages structure and that human discovery and product judgment remain required.

### What warrants review

Review `/skills/outcome-engineering/SKILL.md` for whether the trigger description is sufficiently clear and whether it should live in this repo long-term or be installed as a global Codex skill.

### Future work

Consider adding JSON output for `oe context` once agents need a stable machine-readable contract.

