---
name: oe-cli
description: Use this skill whenever a repository has an Outcome Engineering product graph, the `oe` CLI, the `outcome-engineering` Python package, or the user asks about product vision, strategy, ICPs (ideal customer profiles), outcomes, opportunities, solutions, assumption tests, PRDs, product discovery, or implementing work that should trace to product intent. This skill tells agents how to use `oe` to inspect, create, validate, and contextualize product graph structure before doing product or delivery work.
---

# Outcome Engineering

Use the `oe` CLI to work with repo-native product graphs.

The Python package is `outcome-engineering`. The command is `oe`.

Install the bundled skill for agent tools:

```sh
uvx outcome-engineering install --skills
uvx outcome-engineering install --skills=agents
```

Outcome Engineering stores product intent as a filesystem graph rooted at:

```text
product/
```

The graph convention is:

```text
product/
  VISION.md
  STRATEGY.md
  strategies/
    <strategy>/
      STRATEGY.md
  icps/
    <icp>/
      ICP.md
  outcomes/
    <outcome>/
      OUTCOME.md
      opportunities/
        <opportunity>/
          OPPORTUNITY.md
          opportunities/
            <sub-opportunity>/
          solutions/
            <solution>/
              SOLUTION.md
              assumption-tests/
                <assumption-test>/
                  ASSUMPTION_TEST.md
              prds/
                <prd>/
                  PRD.md
```

Strategies are top-level product context. The simple graph may use `product/STRATEGY.md`; historical or planned strategies may live under `product/strategies/<slug>/STRATEGY.md`. A strategy must declare `name`, `starts`, and `ends` in frontmatter, and status is derived from those dates rather than written. Strategy periods must not overlap.

Assumption tests are the unified concept for the assumptions a solution depends on and the work done to test them (following Continuous Discovery Habits, which does not model experiments separately). They live under solutions. Do not create assumption tests directly under opportunities.

All graph metadata lives in Markdown frontmatter. Fenced YAML metadata blocks are invalid.

An ICP (ideal customer profile) is the "who" the graph serves. A graph can have one or more. ICPs are not part of the outcome → opportunity → solution trace chain, so they do not nest under another node; they live in the top-level `icps/` collection. Outcomes and opportunities declare which ICPs they serve by listing icp ids in frontmatter:

```md
---
type: outcome
id: outcome.<slug>
icps:
  - icp.<slug>
status: draft
---
```

`oe context` resolves these references and surfaces the ICPs a node serves, including ones inherited from outcome or opportunity ancestors.

## When To Use

Use this skill when the user asks to:

- create or refine product vision, strategy, outcomes, opportunities, solutions, assumption tests, or PRDs
- decide what to build next
- turn product thinking into a PRD or delivery work
- implement a feature that should trace back to product intent
- validate or inspect an existing product graph
- add discovery evidence or assumption tests

Skip it for isolated implementation chores that do not affect product behavior, such as small refactors, formatting, dependency bumps, or mechanical bug fixes with no product artifact.

## Default Workflow

Start by checking whether the repo has a product graph:

```sh
test -d product && uv run oe validate product
```

If the graph exists, inspect it before making product or delivery changes:

```sh
uv run oe tree product
uv run oe list outcomes --root product
```

Before working on a specific product artifact, trace it:

```sh
uv run oe trace <node-id-or-slug> --root product
uv run oe context <node-id-or-slug> --root product
```

Use `oe context` before writing a PRD, editing a solution, or implementing code from a PRD. It gives deterministic context; it does not replace reading the linked files.

After changing graph structure, validate:

```sh
uv run oe validate product
```

## Product Judgment Guardrails

`oe validate` only checks structure. When creating or editing graph content, also check the product logic:

- Outcomes describe changed customer, user, product, or business behavior. They are not shipped artifacts, features, documents, graph nodes, or implementation tasks.
- Measures should prove the outcome happened. Prefer behavior, decision quality, retention, learning, risk reduction, or value creation over counts of outputs created.
- Opportunities describe customer needs, pains, constraints, moments, or unmet jobs. Do not hide solution ideas inside opportunities. Candidate artifacts such as essays, examples, guided flows, onboarding sessions, UI panels, automations, prompts, or features belong under `solutions/`.
- Solutions describe the chosen intervention for an opportunity. Assumption tests live under solutions and test desirability, usability, feasibility, viability, or strategic assumptions.
- Known means observed, validated, already decided strategy, or factual graph context. Do not label hopes, beliefs, market theses, or plausible causal stories as known unless there is evidence or an explicit strategic decision behind them.
- Unknown means a genuine uncertainty that should change what gets explored, tested, built, or prioritized next.
- Keep a visible narrative thread: vision -> strategy -> ICP -> outcome -> opportunity -> solution -> assumption test / PRD. If a child node does not make its parent more actionable, revise, move, or delete it.
- Preserve the current wedge deliberately. Broad visions may include teams, but the active strategy should make clear why solo builders are the first adoption path and how that can expand later.

## CLI Commands

Keep this section in sync with `uv run oe --help` and `src/outcome_engineering/cli.py`.

- `uv run oe validate [product]` validates a product graph root.
- `uv run oe tree [product]` prints the graph tree.
- `uv run oe serve [product] --host 127.0.0.1 --port 8000 --open/--no-open` serves the editable local web UI for adding, editing, removing, and visualizing graph nodes.
- `uv run oe list [kind] --root product` lists graph nodes, optionally by kind.
- `uv run oe show <node-id-or-slug> --root product` prints a node's marker file.
- `uv run oe trace <node-id-or-slug> --root product` shows where a node sits in the graph.
- `uv run oe context <node-id-or-slug> --root product` prints deterministic agent context, including trace, ICPs, children, supporting files, ancestor content, ICP content, and node content.
- `uv run oe new <kind> <slug> --root product --under <parent> --title <title>` creates a node in a valid graph location.
- `uv run oe create-example --output examples/delegation-product-graph --force` creates the bundled example graph.
- `uv run oe install --skills` or `uv run oe install --skills=agents` installs bundled assets through the legacy install command.
- `uv run oe install-skill --agent codex|claude|all --target <dir> --force` installs the bundled Outcome Engineering agent skill.

## Creating Nodes

Create graph nodes through `oe new` instead of hand-rolling directories.

```sh
uv run oe new icp <slug> --root product
uv run oe new strategy <slug> --root product
uv run oe new outcome <slug> --root product
uv run oe new opportunity <slug> --root product --under outcome.<slug>
uv run oe new solution <slug> --root product --under opportunity.<slug>
uv run oe new assumption-test <slug> --root product --under solution.<slug>
uv run oe new prd <slug> --root product --under solution.<slug>
```

If a slug is ambiguous, use the full node id or marker file path.

## Important Boundary

`oe` currently manages deterministic structure. It does not make product judgment.

Do not pretend that `oe validate` means the product thinking is good. It only means the graph structure is valid. Human judgment and user discovery remain required.
