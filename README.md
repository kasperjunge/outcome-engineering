# Outcome Engineering

Outcome Engineering is a framework for helping humans continuously challenge product thinking and invent valuable solutions that users and customers actually want, use, and pay for, in ways that work for the business.

The core claim:

> Product development should be modeled as a living intent graph where every product bet can be traced upward to its strategic purpose, downward to implementation, and sideways to the evidence and learning that shaped it.

Traceability is the mechanism. Better product judgment and better product outcomes are the point.

The graph provides structure for product work and gives agents a way to understand, organize, and challenge what is happening.

The framework connects product vision, strategy, OKRs, outcomes, opportunity solution trees, assumptions, experiments, PRDs, user stories, acceptance criteria, code, tests, and evidence into one coherent system.

It is not a replacement for human product judgment. Humans still set direction, talk to users, interpret nuance, and make decisions. Agentic engineering can help maintain structure, reframe opportunities, analyze assumptions, challenge output-thinking, expose what is known and unknown, generate options, implement code, run tests, and preserve traceability across the system.

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

## Repository Structure

- [docs/framework.md](docs/framework.md) defines the framework.
- [docs/graph.md](docs/graph.md) describes the concept graph.
- [docs/glossary.md](docs/glossary.md) defines the core terms.
- [docs/example-structure.md](docs/example-structure.md) explains the example filesystem graph.

## CLI

Run the current CLI locally:

```sh
uv run oe validate examples/delegation-product-graph
uv run oe tree examples/delegation-product-graph
uv run oe list solutions --root examples/delegation-product-graph
uv run oe trace solution.agent-central --root examples/delegation-product-graph
uv run oe show solution.agent-central --root examples/delegation-product-graph
uv run oe context solution.agent-central --root examples/delegation-product-graph
uv run oe create-example --force
uv run oe install --skills --force
uv run oe install --skills=agents --force
uv run oe install-skill --agent codex --force
uv run oe install-skill --agent claude --force
uv run oe install-skill --agent all --force
```

Create nodes deterministically:

```sh
uv run oe new outcome delegation-confidence --root product
uv run oe new opportunity agents-lack-safe-access --root product --under outcome.delegation-confidence
uv run oe new solution agent-central --root product --under opportunity.agents-lack-safe-access
uv run oe new assumption operation-discovery-reduces-tool-overload --root product --under solution.agent-central
uv run oe new experiment fake-connector-prototype --root product --under assumption.operation-discovery-reduces-tool-overload
```

The stable convention for real product repositories is to store the graph at:

```text
product/
```
