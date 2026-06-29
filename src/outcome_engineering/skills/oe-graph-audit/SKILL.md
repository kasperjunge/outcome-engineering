---
name: oe-graph-audit
description: Use this skill when asked to audit, review, critique, or check an Outcome Engineering product graph for method quality, including outcome/output separation, opportunity/solution separation, known/unknown discipline, assumption-test placement, ICP fit, narrative coherence, and whether the graph tells a consistent product story.
---

# OE Graph Audit

Audit an Outcome Engineering product graph for product-thinking quality. This complements `oe validate`, which checks structure only.

## Workflow

1. Run structural checks:

```sh
uv run oe validate product
uv run oe tree product
uv run oe list --root product
```

2. Read the relevant marker files. For a full-graph audit, read `product/VISION.md`, the active strategy, ICPs, outcomes, opportunities, solutions, assumption tests, and PRDs.

3. Use `uv run oe context <node-id> --root product` when auditing a specific node or chain.

4. Report findings by severity, with file and line references when possible. Separate structural validity from product-method quality.

## Audit Checks

- Outcome/output separation: outcomes must describe changed behavior, value, decision quality, learning, risk reduction, adoption depth, or business/customer result. Flag outcomes that are merely artifacts shipped, features built, documents written, graph nodes created, tasks completed, or implementation milestones.
- Measure quality: measures should prove the outcome, not count activity. Prefer evidence of changed behavior or decision impact over counts of outputs.
- Opportunity/solution separation: opportunities must describe needs, pains, constraints, situations, or unmet jobs. Flag solution artifacts inside opportunity titles, body, evidence, or unknowns, including essays, examples, guided flows, onboarding sessions, UI panels, automations, prompts, features, pages, documents, or specific channels.
- Solution placement: solution ideas belong in `solutions/` under an opportunity. Assumption tests belong under solutions, not under opportunities.
- Known/unknown discipline: `Known` is for observed evidence, validated learning, explicit strategic decisions, or factual graph context. `Unknown` is for genuine uncertainty that should affect discovery, testing, prioritization, or delivery. Flag hypotheses, hopes, market theses, causal guesses, or solution preferences mislabeled as known.
- Evidence honesty: distinguish evidence from hypothesis. If there is no customer/user evidence yet, say that plainly.
- ICP consistency: outcomes and opportunities should clearly serve the referenced ICPs, and the pain should sound specific to those people rather than generic users.
- Narrative thread: check whether vision -> strategy -> ICP -> outcome -> opportunity -> solution -> assumption test / PRD forms a believable story. Flag child nodes that repeat the parent, jump levels, contradict the strategy, or fail to make the parent more actionable.
- Wedge coherence: broad visions may include future teams, but the active strategy should explain why the current wedge is first and how expansion could follow.
- Authenticity: the language should sound like the product's actual belief system and target user's lived problem, not generic product-management ceremony.

## Output Format

Keep the audit direct:

- Start with whether `oe validate` passed.
- List findings first, ordered by severity.
- Include concrete fix recommendations.
- Call out strong parts of the graph so the user knows what to preserve.
- End with the highest-leverage next changes.
