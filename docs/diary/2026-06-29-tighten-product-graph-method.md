# Diary: Tighten product graph method discipline

This work tightened the current product graph around Outcome Engineering method quality and added reusable agent guidance for future audits.

## Step 1: Remove solution leakage and add audit guardrails

**Author:** main

### Prompt Context

**Verbatim prompt:** Eliminate "3. Some opportunities contain solution hypotheses too early". And think about a way we can make sure that is not happening again. It is essential that output and outcome gets decoupled. We want to be strick about that.
Regarding 5, we also need to be really strict about decoupling known and unknown and make sure that the graph stays true to that.
And yes, what can we do about 6. The idea is to strat wiht solo builders, because it is more easy to make them users and then advance to temas.

Could we add these principles to the oe-cli skill so that the agent has this thinking while using it and buidling the grraph w the user. And could we make a skill that runs a check like this, and fx checks for true decoupling of output/outcome, known/unknown, consistency in graph narrative and story etc. 

Fix the stuff i mentioned and tell me what you think about the initiavies i told you about
**Interpretation:** The product graph should be edited to remove solution hypotheses from opportunities, tighten outcome/output and known/unknown separation, and clarify the solo-builder wedge. The reusable OE skills should also encode these principles, with a dedicated graph-audit skill for future checks.
**Inferred intent:** Preserve the integrity of the Outcome Engineering method so agents do not accidentally turn the product graph into a feature backlog or a collection of untested claims.

### What I did

I updated `/product/VISION.md` to say Outcome Engineering serves builders and teams, then explicitly explains why the current adoption wedge starts with solo builders before expanding to teams.

I revised `/product/outcomes/first-committed-practitioners/OUTCOME.md` so measures focus on return behavior, decision impact, product intent staying connected to implementation, and learning signals rather than graph creation or output counts.

I removed solution-shaped hypotheses from opportunity files under `/product/outcomes/first-committed-practitioners/opportunities/`, including guided-session, essay, public-graph-example, and channel-specific language. I also renamed the child opportunity from `opportunity.familiar-examples` to `opportunity.concrete-reference-points` so it names the underlying need instead of a likely artifact.

I added Product Judgment Guardrails to both `/skills/oe-cli/SKILL.md` and `/src/outcome_engineering/skills/oe-cli/SKILL.md`.

I created a new bundled `/skills/oe-graph-audit/SKILL.md` and matching `/src/outcome_engineering/skills/oe-graph-audit/SKILL.md`, then added `oe-graph-audit` to `SKILL_NAMES` in `/src/outcome_engineering/skill_installer.py` so it installs with bundled skills.

I validated with `uv run oe validate product`, `uv run oe tree product`, `uv run pytest tests/test_graph.py -q`, a `diff` check between bundled skill copies, and targeted `rg` scans for obvious solution-artifact wording in opportunity content.

### Why

The user wanted strict decoupling between outcomes and outputs, opportunities and solutions, and knowns and unknowns. Encoding this in both the graph and the skills makes the current graph cleaner and makes future agent work less likely to regress into common product-method mistakes.

### What worked

The existing graph structure made the edits straightforward. `oe validate` caught structural issues, while targeted text scans helped find remaining artifact-shaped wording after the first pass. The installer already supported multiple bundled skills through `SKILL_NAMES`, so adding the audit skill was minimal.

### What didn't work

The first pass still left `familiar-examples` as a solution-shaped opportunity, which showed up during the targeted scan. I corrected it by renaming the node and reframing the opportunity around concrete reference points.

### What I learned

The graph's story is strongest when the solo-builder wedge is treated as a strategic adoption path rather than a contradiction with the broader team-oriented vision. The current CLI validates structure only, so method-quality checks need to live in agent guidance or future deterministic linting.

### What was tricky

Some language can be both a real user need and a hidden solution. "Examples" is a good case: users do need concreteness, but "examples" already implies an artifact. Reframing it as "concrete reference points" preserves the need while leaving room for multiple solutions.

### What warrants review

Review `/product/outcomes/first-committed-practitioners/OUTCOME.md` and the opportunity files under `/product/outcomes/first-committed-practitioners/opportunities/` for whether the new wording is strict enough. Also review `/skills/oe-graph-audit/SKILL.md` to decide whether it should remain an agent-only audit skill or become the basis for a future deterministic `oe audit` command.

### Future work

A future `oe audit` or `oe lint-method` command could provide heuristic warnings for output-shaped outcomes, solution-shaped opportunities, and weak known/unknown language. That should complement, not replace, the agent audit skill because narrative coherence and authenticity still require judgment.
