# Diary: Hosted read-only product graph

This records the product graph update for a hosted, authenticated, read-only graph view.

## Step 1: Add opportunity, solution, and PRD

**Author:** main

### Prompt Context

**Verbatim prompt:** yes i love that. Please make the opportunity, the solution, and the PRD
**Interpretation:** Add the reviewed opportunity and solution to the Outcome Engineering product graph, then create the PRD under the solution instead of using the generic root-level PRD folder from the PRD skill.
**Inferred intent:** Preserve the strategic reasoning in the product graph so future implementation work traces from the current outcome through the user need and solution.

### What I did

I created a worktree branch at `.worktrees/hosted-read-only-product-graph` from `main`. I used `uv run oe new` to create `/product/outcomes/first-committed-practitioners/opportunities/everyone-sees-same-product-direction/OPPORTUNITY.md`, `/product/outcomes/first-committed-practitioners/opportunities/everyone-sees-same-product-direction/solutions/hosted-read-only-product-graph/SOLUTION.md`, and `/product/outcomes/first-committed-practitioners/opportunities/everyone-sees-same-product-direction/solutions/hosted-read-only-product-graph/prds/hosted-read-only-product-graph/PRD.md`.

I replaced the generated placeholders with the approved opportunity framing: the user need is that solo builders and small founder teams need everyone to see the same product direction without local setup. I captured the solution as a hosted, authenticated, read-only graph from the repo's current `main` branch, and the PRD as the product requirements for that read-only hosted graph.

I validated the graph with `uv run oe validate product`, which returned `OK: product is a valid product graph`, and checked the graph placement with `uv run oe tree product`.

### Why

The current strategy says the graph should be visually usable and help users stay aligned with the vision. This work adds a more specific opportunity for persistent shared access, while keeping the first hosted version read-only so the repo remains the source of truth.

### What worked

The `oe new` commands created the expected graph structure cleanly under `outcome.first-committed-practitioners`. The final graph validated without structural errors.

### What didn't work

No command failed during this step.

### What I learned

The request is not primarily for another graph editor. The first user value is a persistent browser-accessible alignment surface, with editing intentionally deferred.

### What was tricky

The opportunity needed to avoid being a solution in disguise. The final wording frames the need as shared product direction without setup, leaving hosted graph access as one solution to that need.

### What warrants review

Review the new opportunity, solution, and PRD under `/product/outcomes/first-committed-practitioners/opportunities/everyone-sees-same-product-direction/`. Validate with `uv run oe validate product` and inspect the placement with `uv run oe tree product`.

### Future work

Future implementation planning should decide how the hosted read-only graph is deployed, how it authenticates users, and how it stays in sync with `main`.
