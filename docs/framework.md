# Framework

Outcome Engineering is a way to help humans continuously challenge product thinking and invent valuable solutions that users and customers actually want, use, and pay for, in ways that work for the business.

It does this by structuring product development as a traceable graph of intent, discovery, delivery, evidence, and learning.

It starts from the belief that product work should preserve meaning across levels of abstraction. A line of code should be explainable in terms of the user behavior it enables, the acceptance criteria it satisfies, the story it implements, the opportunity it serves, the outcome it is intended to move, and the product vision it supports.

The inverse should also be true: a product vision should be traceable downward into the concrete bets, decisions, stories, tests, and code that attempt to realize it.

## Core Principle

Every node in the product development graph is a belief until supported by evidence.

This includes beliefs such as:

- This vision is compelling.
- This strategy is the right strategic choice.
- This objective matters now.
- This key result measures meaningful progress.
- This outcome is worth pursuing.
- This opportunity is real.
- This solution addresses the opportunity.
- This assumption is risky.
- This experiment will produce useful learning.
- This user story expresses the right behavior.
- This acceptance criterion captures success.
- This implementation satisfies the intended behavior.
- This release changed something meaningful.

## Human Discovery

Outcome Engineering assumes that humans must keep talking to users.

AI agents can help prepare interviews, synthesize notes, inspect patterns, analyze assumptions, draft experiments, connect artifacts, and implement software. They should not become an excuse for teams to stop direct human contact with customers and users.

Qualitative discovery is not optional. It is how teams understand context, motivation, language, emotion, constraint, and causality. Quantitative data is useful, but it is not sufficient on its own.

## Agentic Engineering

Agentic engineering can operate across the graph:

- Discovery support: summarize interviews, compare signals, surface assumptions, propose experiments.
- Product support: maintain OSTs, connect outcomes to opportunities, draft PRDs, check traceability.
- Delivery support: break stories into tasks, write code, produce tests, review implementation.
- Learning support: compare evidence to assumptions, detect stale beliefs, suggest graph updates.

The goal is not autonomous product management. The goal is a structured system where agents help humans preserve product intent and move faster without collapsing discovery into delivery.

## Evidence Is Distributed

Evidence is not only generated after a feature is released.

Evidence can attach to any node:

- A user conversation can produce evidence about an opportunity.
- A prototype test can produce evidence about a solution.
- An assumption test can produce evidence about risk.
- A technical spike can produce evidence about feasibility.
- A usability test can produce evidence about a workflow.
- A released product can produce evidence about behavior change.
- Telemetry can produce evidence about scale and frequency.

Learning can update any part of the graph. A discovery interview might update an opportunity. A failed prototype might update a solution. A technical constraint might update the PRD. Production data might update the outcome model. A strategy review might update the OKR hierarchy.

## Output, Behavior, Outcome, Learning

Outcome Engineering keeps these concepts distinct:

- Output: what the team ships.
- Behavior: what users or customers do differently.
- Outcome: the measurable change the team is trying to create.
- Learning: what the team now believes differently because of evidence.

This distinction prevents the system from mistaking task completion for product progress.

## Traceability Standard

The graph should support two questions:

1. Looking downward: what delivery work and evidence currently support this product intent?
2. Looking upward: why does this artifact, decision, test, or line of code exist?

If either question cannot be answered, the graph has a gap.
