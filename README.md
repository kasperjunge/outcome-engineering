# Outcome Engineering

Outcome Engineering helps teams stay aligned on the single most important thing to work on to drive an outcome toward a larger vision.

It is a method and toolset for turning messy product thinking into a traceable, actionable product graph. The graph connects vision, strategy, outcomes, opportunities, solutions, assumptions, experiments, evidence, PRDs, acceptance tests, and code so humans and agents can reason about what to do next.

The point is not documentation for its own sake. The point is faster, more efficient, and more consistent motion toward product-market fit, business value, and customer value.

## What It Helps You Do

Outcome Engineering is designed to be useful from any messy product entry point, then grow a coherent graph around it.

### Challenge assumptions

Paste messy product thinking into an agent and ask it to expose the hidden or risky assumptions. This helps teams validate earlier instead of building too long on beliefs that may not survive contact with customers, users, the market, the business, or technical reality.

### Craft vision and strategy

Use an agent to clarify the top of the graph: vision, strategy, outcomes, and focus. This helps teams avoid confusing outputs with outcomes and keeps product work aligned around the highest-leverage next step.

### Challenge product intent

Bring a PRD, spec, issue, idea, code change, or acceptance test and challenge whether it traces upward to an opportunity, outcome, strategy, and vision. This helps prevent delivery work from drifting away from product intent.

See [docs/agent-entry-points.md](docs/agent-entry-points.md) for the recommended agent-native starting points.

## The Core Claim

Product development should be modeled as a living intent graph where every product bet can be traced upward to its strategic purpose, downward to implementation, and sideways to the evidence and learning that shaped it.

Traceability is the mechanism. Better product judgment and better product outcomes are the point.

The graph gives humans a structure for product work and gives agents a context model they can use to understand, organize, and challenge what is happening.

It is not a replacement for human product judgment. Humans still set direction, talk to users, interpret nuance, and make decisions. Agents can help maintain structure, reframe opportunities, analyze assumptions, challenge output-thinking, expose what is known and unknown, generate options, implement code, run tests, and preserve traceability across the system.

Agents can generate plausible opportunities, solutions, assumptions, stories, and analyses, but plausibility is not grounding. Synthetic artifacts remain hypotheses until supported by real customer, user, market, business, or technical evidence.

## The Problem

Most organizations lose intent as work moves through the product development process.

A compelling product vision becomes a strategy deck. Strategy becomes OKRs. OKRs become roadmap items. Roadmap items become tickets. Tickets become code. Code ships. Somewhere along the way, the original customer need, business intent, assumptions, and evidence are often lost.

The result is delivery without memory:

- Teams ship outputs without knowing which outcome they serve.
- Discovery evidence lives separately from delivery work.
- User stories lose their connection to customer opportunities.
- Code becomes hard to explain in product terms.
- Learning arrives too late, or never updates the underlying product model.

Outcome Engineering treats this as a structural problem.

## The Model

At the highest level:

```text
Vision
  -> Strategy
    -> OKRs
      -> Outcomes
        -> Opportunity Solution Trees
          -> Opportunities
            -> Solutions
              -> Assumptions
                -> Experiments
                  -> Decisions
                    -> PRDs
                      -> User Stories
                        -> Acceptance Criteria
                          -> Code
                            -> Tests
                              -> Released Product
```

But this is not a one-way waterfall.

Evidence and learning can happen throughout the graph:

```text
Any product belief
  -> Evidence
    -> Learning
      -> Update the graph
```

Evidence can come from user interviews, customer conversations, sales calls, support conversations, analytics, prototype tests, assumption tests, usability sessions, technical spikes, experiments, production telemetry, and market observation.

Quantitative data can show what is happening. Human discovery is needed to understand why it is happening.

## Start Small

You do not need a complete graph to get value.

Start with the product material you already have: a vague idea, meeting notes, a PRD, a spec, an issue, or a code change. Let an agent structure and challenge it, then keep the useful parts as graph artifacts.

Useful partial graphs matter more than perfect graph completeness.

## Repository Structure

- [product/VISION.md](product/VISION.md) defines the product vision for Outcome Engineering itself.
- [product/STRATEGY.md](product/STRATEGY.md) defines the current product strategy for Outcome Engineering itself.
- [docs/agent-entry-points.md](docs/agent-entry-points.md) describes the first agent-native use cases.
- [docs/framework.md](docs/framework.md) defines the framework.
- [docs/graph.md](docs/graph.md) describes the concept graph.
- [docs/glossary.md](docs/glossary.md) defines the core terms.
- [docs/example-structure.md](docs/example-structure.md) explains the example filesystem graph.

## CLI

The Python package is `outcome-engineering`. The command is `oe`.

Real product repositories should store the graph at:

```text
product/
```

Install the bundled agent skills with Playwright-style project-local commands:

```sh
uv run oe install --skills --force
uv run oe install --skills=agents --force
```

Inspect a product graph:

```sh
uv run oe validate product
uv run oe tree product
uv run oe list outcomes --root product
uv run oe list opportunities --root product
uv run oe list solutions --root product
```

Trace product intent before editing a product artifact or implementing from a PRD:

```sh
uv run oe trace solution.agent-central --root product
uv run oe context solution.agent-central --root product
```

Read a node's canonical marker file:

```sh
uv run oe show outcome.delegation-confidence --root product
uv run oe show opportunity.agents-lack-safe-access --root product
uv run oe show prd.agent-central-mvp --root product
```

Create nodes deterministically:

```sh
uv run oe new outcome delegation-confidence --root product
uv run oe new opportunity agents-lack-safe-access --root product --under outcome.delegation-confidence
uv run oe new assumption customer-pain-is-frequent --root product --under opportunity.agents-lack-safe-access
uv run oe new solution agent-central --root product --under opportunity.agents-lack-safe-access
uv run oe new assumption operation-discovery-reduces-tool-overload --root product --under solution.agent-central
uv run oe new experiment fake-connector-prototype --root product --under assumption.operation-discovery-reduces-tool-overload
uv run oe new prd agent-central-mvp --root product --under solution.agent-central
```

Assumptions can live under opportunities or solutions.
Experiments can only live under assumptions.

Try the example graph:

```sh
uv run oe create-example --force
uv run oe validate examples/delegation-product-graph
uv run oe tree examples/delegation-product-graph
uv run oe context solution.agent-central --root examples/delegation-product-graph
```

Install the skills into explicit global agent-tool locations:

```sh
uv run oe install-skill --agent codex --force
uv run oe install-skill --agent claude --force
uv run oe install-skill --agent all --force
```
