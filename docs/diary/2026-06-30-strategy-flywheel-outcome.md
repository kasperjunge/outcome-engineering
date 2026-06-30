# Diary: strategy flywheel outcome

This records the first product graph step toward treating flywheels as an experimental strategy-level feature in Outcome Engineering.

## Step 1: Add the strategy flywheel outcome

**Author:** main

### Prompt Context

**Verbatim prompt:** Great let's keep the conversational thing because I'm just listening to it. Great I would like to make this an experimental feature and actually I want to think of it as a graph because a flywheel is a graph. It's notes that are kind of like pointing at each other in a circle. Can we design it that way and make it a feature in the outcome engineering framework, the graph, and the UI? Let's start talking about that with the aim of actually making this a PRD with a solution and an opportunity for it. Also I think we need to make an outcome for this, right? We need to design a PRD for this and make it fit into the product graph

Then: I love it. Please create a new outcome for this. Just make a work tree for it and get started. I really like this idea

**Interpretation:** Add a new top-level product outcome for flywheel thinking before creating the supporting opportunity, solution, and PRD.
**Inferred intent:** Keep the existing product graph clean while creating a proper strategic home for an experimental flywheel graph feature.

### What I did

I created the `/product/outcomes/builders-understand-strategy-flywheel/` node through `uv run oe new outcome builders-understand-strategy-flywheel --root product`, then replaced the generated placeholder text in `/product/outcomes/builders-understand-strategy-flywheel/OUTCOME.md`.

The outcome is titled "Builders understand how their strategy compounds" and frames the changed state as solo builders being able to explain their reinforcing strategic motion, identify weak links, and connect flywheel insight back to concrete product decisions.

I validated the graph with `uv run oe validate product` and inspected the structure with `uv run oe tree product`.

### Why

The flywheel should not be modeled as a normal outcome, opportunity, solution, or PRD node. It is a strategy-level causal graph. Adding a top-level outcome gives the future feature work a proper product intent: improving builder strategy quality, not merely shipping a flywheel UI.

### What worked

`oe new` created the correct graph structure and marker file. `uv run oe validate product` passed after the outcome copy was updated.

### What didn't work

No implementation errors occurred. One small workflow detail: `git diff -- product/outcomes/builders-understand-strategy-flywheel/OUTCOME.md` showed nothing because the outcome directory is still untracked.

### What I learned

The cleanest framing is that the product graph explains what the builder is pursuing, while the flywheel explains why the strategy can compound. That distinction keeps the existing trace chain intact.

### What was tricky

The outcome needed to avoid describing the feature as an output. "Experimental flywheel graph" is likely a solution; the outcome is the builder's improved ability to understand and use compounding strategic logic.

### What warrants review

Review `/product/outcomes/builders-understand-strategy-flywheel/OUTCOME.md` for whether the measures are strong enough and whether the outcome should reference solo builders only or leave room for teams later.

Validate with:

```sh
uv run oe validate product
uv run oe tree product
```

### Future work

Add a customer-shaped opportunity under this outcome, then a solution for an experimental flywheel graph surface, then a PRD for the smallest useful markdown-backed and UI-rendered flywheel feature.

## Step 2: Add the flywheel opportunity, solution, assumption test, and PRD

**Author:** main

### Prompt Context

**Verbatim prompt:** Great! Have you used the OEE best practices to do it, the skill? If not please make sure that the outcome aligns with that and then use the skill to also create the rest of the nodes, all the way down to the PRD and everything for the flywheel thing

**Interpretation:** Apply the Outcome Engineering best-practices skill explicitly, verify the outcome, and create the supporting graph chain down to a PRD.
**Inferred intent:** Turn the flywheel idea into a complete, semantically clean product graph slice that can guide later implementation.

### What I did

I read `/src/outcome_engineering/skills/oe-best-practices/SKILL.md` and the references for outcomes, opportunities, solutions, assumption tests, and PRDs. I added the solo-builder ICP reference to `/product/outcomes/builders-understand-strategy-flywheel/OUTCOME.md` because the outcome is explicitly scoped to that ICP.

I created these nodes with `oe new`:

- `/product/outcomes/builders-understand-strategy-flywheel/opportunities/strategy-compounding-is-hard-to-see/OPPORTUNITY.md`
- `/product/outcomes/builders-understand-strategy-flywheel/opportunities/strategy-compounding-is-hard-to-see/solutions/experimental-flywheel-graph/SOLUTION.md`
- `/product/outcomes/builders-understand-strategy-flywheel/opportunities/strategy-compounding-is-hard-to-see/solutions/experimental-flywheel-graph/assumption-tests/flywheel-visualization-improves-strategy-clarity/ASSUMPTION_TEST.md`
- `/product/outcomes/builders-understand-strategy-flywheel/opportunities/strategy-compounding-is-hard-to-see/solutions/experimental-flywheel-graph/prds/experimental-flywheel-graph-mvp/PRD.md`

I wrote the opportunity as the customer need "I need to see how my strategy compounds," the solution as an optional strategy-level flywheel graph, the assumption test as a prototype comparison against prose-only strategy, and the PRD as the first experimental flywheel graph MVP.

I validated with `uv run oe validate product`, inspected with `uv run oe tree product`, and checked the full PRD context with `uv run oe context prd.experimental-flywheel-graph-mvp --root product`.

### Why

The feature should trace from a changed builder outcome through a customer-shaped need before becoming an implementation idea. The PRD needs the strategy flywheel idea to remain separate from the normal product graph while still becoming visible, editable, and agent-legible.

### What worked

The graph conventions handled the new slice cleanly: outcome -> opportunity -> solution -> assumption test / PRD. The flywheel itself remains a proposed product artifact inside the solution and PRD, not a new graph node kind yet.

### What didn't work

No validation errors occurred. The main risk is product semantic drift: the PRD acceptance criteria discuss flywheel artifact structure, but the exact artifact location remains open because that should be decided during implementation design.

### What I learned

The best-practices distinction clarified the model: the flywheel graph feature is a solution, while the user need is seeing compounding strategy logic, and the outcome is improved strategy judgment.

### What was tricky

The phrase "flywheel graph" can sound like it belongs inside the graph model. For now, it is cleaner to describe it as a separate strategy-level graph surface that the normal product graph can point to through product intent.

### What warrants review

Review the PRD open questions before implementation, especially whether the artifact should be `product/FLYWHEEL.md` or `product/flywheels/<slug>/FLYWHEEL.md`.

Validate with:

```sh
uv run oe validate product
uv run oe context prd.experimental-flywheel-graph-mvp --root product
```

### Future work

Decide the flywheel artifact shape and UI entry point, then implement the smallest version that can be rendered visually and included in agent strategy context.
