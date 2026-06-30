# Diary: oe-best-practices skill

Created the first version of an Outcome Engineering best-practices skill, starting with slim opportunity guidance.

## Step 1: Add opportunity best-practices skill

**Author:** main

### Prompt Context

**Verbatim prompt:** "i want to call it oe-best-practices.
Use this skill to write the skill:
$writing-great-skills 

We're doing it in steps, right?
1. Build this skill. The main body should be very short and then it should just basically align or direct to some lookup that actually defines each of those, right?
2. Let's start with opportunities so make them very slim. Follow the writing great skills best practices and let's only start with the opportunity one.
3. This skill should be stored in the outcome engineering repository."

**Interpretation:** Create a new `oe-best-practices` skill in the Outcome Engineering repo, keep the root `SKILL.md` short, and place the initial opportunity-specific rules in disclosed reference material.

**Inferred intent:** Establish a single source of truth for semantic product-graph guidance so humans and agents can keep node content clean.

### What I did

I created a worktree at `/.worktrees/oe-best-practices` on branch `oe-best-practices`. I added `/skills/oe-best-practices/SKILL.md` and `/skills/oe-best-practices/references/opportunities.md`, then mirrored the same files under `/src/outcome_engineering/skills/oe-best-practices/` so the package can install the bundled skill. I updated `/src/outcome_engineering/skill_installer.py` to include `oe-best-practices` in `SKILL_NAMES`.

### Why

The skill needs to follow progressive disclosure: a short top-level workflow plus references loaded only for the relevant node type. The source copy is needed for package installation, and the root `skills/` copy matches the repo's current skill editing convention.

### What worked

The short skill body cleanly routes to `references/opportunities.md`. `uv run oe validate product` passed, `uv run pytest` passed, and a temporary `copy_skills` install confirmed both `SKILL.md` and `references/opportunities.md` are copied.

### What didn't work

The first check showed the installer has an explicit whitelist:

```text
SKILL_NAMES = (SKILL_NAME, "oe-grill", "oe-graph-audit", "oe-release", "oe-validate")
```

Without updating that tuple, `oe-best-practices` would exist in source but would not be installed by the bulk skill installer.

### What I learned

Bundled Outcome Engineering skills are not discovered dynamically. New installable skills must be added to `/src/outcome_engineering/skill_installer.py`.

### What was tricky

This skill is the first bundled skill with a nested reference file in this repo, so it needed an explicit install smoke test rather than only file creation and unit tests.

### What warrants review

Review `/skills/oe-best-practices/references/opportunities.md` for product-method accuracy, especially the boundary between opportunities and outcomes or solutions. Validate installation behavior with `uv run pytest` and a temporary `copy_skills` smoke test.

### Future work

Add references for outcomes, solutions, strategy, and vision as separate disclosed files instead of expanding the main skill body.

## Step 2: Add outcome best-practices reference

**Author:** main

### Prompt Context

**Verbatim prompt:** "I really like those. Please however one I also want to add is: no, let's just please just write that one down on how to write outcomes. I like it"

**Interpretation:** Add the reviewed outcome-writing guidance to the `oe-best-practices` skill as a concise reference file.

**Inferred intent:** Expand the skill one node type at a time while keeping each reference short and reviewable.

### What I did

I added `/skills/oe-best-practices/references/outcomes.md` and mirrored it at `/src/outcome_engineering/skills/oe-best-practices/references/outcomes.md`. I added an outcomes pointer to both `SKILL.md` files. I did not re-add examples to the opportunities reference after the user removed them.

### Why

The skill body should remain a router, while each product-graph concept gets its own slim reference. Outcomes needed their own contract separate from opportunity guidance.

### What worked

`uv run oe validate product` passed and `uv run pytest` passed with 47 tests.

### What didn't work

Nothing failed in this step.

### What I learned

The best-practices references should stay example-free unless the user explicitly wants examples. The useful core is the small set of rules.

### What was tricky

The user had edited the opportunity reference manually, so I checked the file before patching and avoided overwriting that change.

### What warrants review

Review `/skills/oe-best-practices/references/outcomes.md` for whether the six rules are concise enough and whether the definition is the right level of breadth for Outcome Engineering.

### Future work

Continue with separate references for solutions, strategy, and vision.

## Step 4: Add vision best-practices reference

**Author:** main

### Prompt Context

**Verbatim prompt:** "Okay so you just said a very not very nice word there, roadmap. We need to delete that. That's what in Danish is called a Fy-År. We don't want that word. That's not a concept that we're working with. Otherwise I love it. Please add it"

**Interpretation:** Add the reviewed product-vision guidance, but avoid the banned term and use OE language instead.

**Inferred intent:** Keep OE best-practices terminology clean and aligned with the product's conceptual model.

### What I did

I added `/skills/oe-best-practices/references/vision.md` and mirrored it at `/src/outcome_engineering/skills/oe-best-practices/references/vision.md`. I added a vision pointer to both `SKILL.md` files. I checked the new best-practices skill for the banned term with `rg -n "roadmap|Roadmap" skills/oe-best-practices src/outcome_engineering/skills/oe-best-practices`.

### Why

Vision needed its own concise contract, and OE should distinguish vision from strategy and delivery without importing concepts the product deliberately avoids.

### What worked

The banned term did not appear in the new best-practices skill. `uv run oe validate product` passed and `uv run pytest` passed with 47 tests.

### What didn't work

Nothing failed in this step. The `rg` check exited with code 1 because it found no matches, which was the expected result.

### What I learned

The skill should use OE-native language like strategy and delivery instead of generic product-management terms that the project does not want to carry.

### What was tricky

The vision rule about separation needed to avoid the banned term while still making the boundary clear.

### What warrants review

Review `/skills/oe-best-practices/references/vision.md`, especially rule 4, to confirm "delivery" is the right replacement term.

### Future work

Continue with separate references for solutions and strategy.

## Step 5: Add strategy best-practices reference

**Author:** main

### Prompt Context

**Verbatim prompt:** "Sounds great! Please make the decoupling very clear and add that to the best practices on how to write a strategy"

**Interpretation:** Add the reviewed strategy-writing rules and make the boundary between strategy and outcomes explicit.

**Inferred intent:** Prevent strategy artifacts from becoming outcomes, delivery lists, or vague ambition by defining strategy as the current bet.

### What I did

I added `/skills/oe-best-practices/references/strategy.md` and mirrored it at `/src/outcome_engineering/skills/oe-best-practices/references/strategy.md`. I added a strategy pointer to both `SKILL.md` files. Rule 5 explicitly states that strategy translates vision into a current bet, while outcomes are the changed states that prove whether the bet works.

### Why

Strategy and outcomes are easy to blur. The skill needs a compact boundary rule so agents know when they are writing the bet versus writing proof that the bet worked.

### What worked

`uv run oe validate product` passed and `uv run pytest` passed with 47 tests.

### What didn't work

Nothing failed in this step.

### What I learned

"Strategy is the bet; outcome is the proof" is the clearest boundary, but the reference uses slightly more formal wording to stay self-contained.

### What was tricky

The rule needed to separate strategy from vision and outcomes at the same time without bloating the reference.

### What warrants review

Review `/skills/oe-best-practices/references/strategy.md`, especially rule 5, for whether the decoupling is sharp enough.

### Future work

Continue with a separate reference for solutions.

## Step 7: Add solution, assumption test, and PRD references

**Author:** main

### Prompt Context

**Verbatim prompt:** "I totally agree with the first one. A solution should reveal its riskiest assumptions. I think it's a great point that the assumption is okay to have in the solution and then the assumptions test is more like: okay what are we doing to actually test these assumptions?

I think it's great. I think it's a clear boundary, great catch. Also in the assumption test it's great with examples but I just want to inspire too that this could really be anything and it's okay to be creative about it. Also yeah, it seems like we're aligned. Please just add these to the OE best practices skill"

**Interpretation:** Add concise best-practices references for solutions, assumption tests, and PRDs, preserving the clarified boundaries.

**Inferred intent:** Complete the OE best-practices chain from vision through PRD while keeping each concept decoupled.

### What I did

I added `/skills/oe-best-practices/references/solutions.md`, `/skills/oe-best-practices/references/assumption-tests.md`, and `/skills/oe-best-practices/references/prds.md`, then mirrored them under `/src/outcome_engineering/skills/oe-best-practices/references/`. I added pointers for solutions, assumption tests, and PRDs to both `SKILL.md` files.

### Why

Solutions need to reveal assumptions without becoming tests. Assumption tests need room for creative evidence-gathering, not only code or analytics. PRDs need a clear why/what boundary while leaving implementation details out.

### What worked

The new references stayed compact and boundary-focused. `uv run oe validate product` passed and `uv run pytest` passed with 47 tests.

### What didn't work

Nothing failed in this step.

### What I learned

The lower graph nodes need explicit "ownership" language: solution owns the intervention and its risky beliefs, assumption tests own the evidence, and PRDs own the why-to-what delivery contract.

### What was tricky

The assumption test reference needed to include examples without making the examples feel exhaustive or prescriptive.

### What warrants review

Review `/skills/oe-best-practices/references/solutions.md`, `/skills/oe-best-practices/references/assumption-tests.md`, and `/skills/oe-best-practices/references/prds.md` for boundary clarity.

### Future work

Review the full best-practices skill as a system and decide whether any node references should include anti-patterns or stay rules-only.

## Step 6: Sharpen boundaries between graph concepts

**Author:** main

### Prompt Context

**Verbatim prompt:** "I love it. Please add it"

**Interpretation:** Add the reviewed boundary sentences to clarify vision versus outcomes and outcomes versus opportunities.

**Inferred intent:** Make the best-practices references more resistant to concept drift without adding more rules.

### What I did

I added a sentence to `/skills/oe-best-practices/references/vision.md` explaining that outcomes prove progress while vision defines the durable future. I added a sentence to `/skills/oe-best-practices/references/opportunities.md` explaining that outcomes describe what changes while opportunities explain where to intervene. I mirrored both changes under `/src/outcome_engineering/skills/oe-best-practices/references/`.

### Why

The four references were already mostly decoupled, but "future state" and "changed state" could blur vision with outcomes, and opportunities could still drift into mini-outcomes without a boundary sentence.

### What worked

The clarification fit as one sentence in each reference. `uv run oe validate product` passed and `uv run pytest` passed with 47 tests.

### What didn't work

Nothing failed in this step.

### What I learned

Boundary language is most useful near the definition, before the rules, because it frames how to read the rest of the reference.

### What was tricky

The edit needed to clarify boundaries without turning the slim references into a comparison matrix.

### What warrants review

Review the opening sections of `/skills/oe-best-practices/references/vision.md` and `/skills/oe-best-practices/references/opportunities.md` to confirm the added sentences are terse enough.

### Future work

Continue with a separate reference for solutions.

## Step 3: Tighten outcome/output separation

**Author:** main

### Prompt Context

**Verbatim prompt:** "great add it"

**Interpretation:** Fold the explicit outcome-versus-output distinction and quantitative-plus-qualitative measurement guidance into the outcome reference.

**Inferred intent:** Make the outcome guidance stricter where users and agents most commonly make mistakes, without bloating the reference.

### What I did

I updated `/skills/oe-best-practices/references/outcomes.md` and the mirrored `/src/outcome_engineering/skills/oe-best-practices/references/outcomes.md`. Rule 1 now hard-separates outcomes from outputs. Rule 4 now recommends both quantitative and qualitative measures where possible.

### Why

Outcome/output confusion is one of the central failure modes for product graphs. Quantitative-only measures can overfit to measurable activity while missing meaning, causality, and whether the change is actually valuable.

### What worked

The list stayed at six rules. `uv run oe validate product` passed and `uv run pytest` passed with 47 tests.

### What didn't work

Nothing failed in this step.

### What I learned

The concise reference can still carry sharper product judgment by strengthening existing rules instead of adding more items.

### What was tricky

The quantitative and qualitative measure guidance needed to be strong without becoming an absolute requirement for every outcome at every stage.

### What warrants review

Review rule 4 in `/skills/oe-best-practices/references/outcomes.md` to decide whether "Prefer both" is the right strength.

### Future work

Continue with separate references for solutions, strategy, and vision.
