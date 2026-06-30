---
name: oe-graph-audit
description: Use this skill when asked to audit, review, critique, or check an Outcome Engineering product graph for method quality, including outcome/output separation, opportunity/solution separation, known/unknown discipline, assumption-test placement, ICP fit, narrative coherence, and whether the graph tells a consistent product story.
---

# OE Graph Audit

Audit an Outcome Engineering product graph for product-thinking quality. This complements `oe validate`, which checks structure only.

Use `oe-cli` for graph inspection commands. Use `oe-best-practices` as the source of truth for judging node content.

## Workflow

1. Run structural checks:

```sh
uv run oe validate product
uv run oe tree product
uv run oe list --root product
```

2. Read the relevant marker files. For a full-graph audit, read `product/VISION.md`, the active strategy, ICPs, outcomes, opportunities, solutions, assumption tests, and PRDs.

3. Use `uv run oe context <node-id> --root product` when auditing a specific node or chain.

4. Read the matching `oe-best-practices` reference for every node type you judge.

5. Report findings by severity, with file and line references when possible. Separate structural validity from product-method quality.

## Audit Checks

- Apply the relevant `oe-best-practices` reference for each node.
- Check cross-node coherence: vision -> strategy -> ICP -> outcome -> opportunity -> solution -> assumption test / PRD should form a believable product story.
- Flag parent/child mismatches: repetition, level jumps, contradictions, generic wording, or children that do not make the parent more actionable.
- Distinguish structural validity from product-method quality.
- Do not invent evidence, customers, metrics, or strategic decisions while recommending fixes.

## Output Format

Keep the audit direct:

- Start with whether `oe validate` passed.
- List findings first, ordered by severity.
- Include concrete fix recommendations.
- Call out strong parts of the graph so the user knows what to preserve.
- End with the highest-leverage next changes.
