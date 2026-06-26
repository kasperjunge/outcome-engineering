---
name: outcome-engineering
description: Use this skill whenever a repository has an Outcome Engineering product graph, an `oe` CLI, or the user asks about product vision, outcomes, opportunities, solutions, assumptions, experiments, PRDs, product discovery, or implementing work that should trace to product intent. This skill tells agents how to use `oe` to inspect, create, validate, and contextualize product graph structure before doing product or delivery work.
---

# Outcome Engineering

Use the `oe` CLI to work with repo-native product graphs.

Outcome Engineering stores product intent as a filesystem graph rooted at:

```text
product/
```

The graph convention is:

```text
product/
  VISION.md
  STRATEGY.md
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
              assumptions/
                <assumption>/
                  ASSUMPTION.md
                  experiments/
                    <experiment>/
                      EXPERIMENT.md
              prds/
                <prd>/
                  PRD.md
```

Experiments belong under assumptions. Do not create experiments directly under solutions.

## When To Use

Use this skill when the user asks to:

- create or refine product vision, strategy, outcomes, opportunities, solutions, assumptions, experiments, or PRDs
- decide what to build next
- turn product thinking into a PRD or delivery work
- implement a feature that should trace back to product intent
- validate or inspect an existing product graph
- add discovery evidence, assumptions, or experiments

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

## Creating Nodes

Create graph nodes through `oe new` instead of hand-rolling directories.

```sh
uv run oe new outcome <slug> --root product
uv run oe new opportunity <slug> --root product --under outcome.<slug>
uv run oe new solution <slug> --root product --under opportunity.<slug>
uv run oe new assumption <slug> --root product --under solution.<slug>
uv run oe new experiment <slug> --root product --under assumption.<slug>
uv run oe new prd <slug> --root product --under solution.<slug>
```

If a slug is ambiguous, use the full node id or marker file path.

## Important Boundary

`oe` currently manages deterministic structure. It does not make product judgment.

Do not pretend that `oe validate` means the product thinking is good. It only means the graph structure is valid. Human judgment and user discovery remain required.

