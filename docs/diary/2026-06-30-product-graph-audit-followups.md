# Diary: Product graph audit follow-ups

This captures the graph changes made after the product-method audit: clarifying the first-user/flywheel boundary, expanding the ICP, adding a hosted read-only graph assumption test, and separating durable vision from current strategy.

## Step 1: Apply audit follow-ups to the product graph

**Author:** main

### Prompt Context

**Verbatim prompt:** 1. The Flywheel thing is a me thing. I'm the first user right now and I want this but the graph should be able to be used without the Flywheel.
2. I agree with the drift here. Let's also make the ICP a small solo, like a small founder team or a small team trying to build something. Let's also make it that.
3. Please add an assumption test to that.
4. This is also basically: I am the first user of this and we're mainly serving my needs right now. That's why there is so little evidence. We need to get to some sort of first version, an MVP, that I can actually convince others to use, I guess. Don't worry too much about number four.
5. Please fix the thing you have identified there to make a clear decoupling and clear boundary between vision and strategy.
6. I agree with the implementation details in PRD. Let's just keep it there because, just for you now, I don't know. Let's just keep it there.

**Interpretation:** The product graph should be updated, not merely reviewed. The flywheel branch should remain optional and framed as a first-user need. The ICP should expand from solo software product builders to small product-building teams. The hosted read-only graph solution needs an assumption test. Vision should become more durable while strategy carries the current wedge, first-user evidence posture, and optional flywheel boundary.

**Inferred intent:** Keep the graph honest about the current dogfooding stage while making it more coherent for future MVP adoption by other small builders and teams.

### What I did

I ran `uv run oe validate product` before changing the graph and confirmed it was valid. I read the `oe-cli` skill and the relevant `oe-best-practices` references for vision, strategy, ICPs, outcomes, opportunities, and assumption tests.

I created a new assumption test with `uv run oe new assumption-test hosted-read-only-graph-repeated-alignment-value --root product --under solution.hosted-read-only-product-graph --title "Hosted read-only graph creates repeated alignment value"` and filled it out under `/product/outcomes/first-committed-practitioners/opportunities/everyone-sees-same-product-direction/solutions/hosted-read-only-product-graph/assumption-tests/hosted-read-only-graph-repeated-alignment-value/ASSUMPTION_TEST.md`.

I renamed the ICP directory from `/product/icps/solo-software-product-builders` to `/product/icps/small-product-building-teams`, changed its id to `icp.small-product-building-teams`, and updated outcome references. I rewrote `/product/VISION.md` to remove current wedge and implementation-surface detail, and moved the current strategic choices into `/product/STRATEGY.md`. I also updated affected outcomes, opportunities, solutions, and the flywheel assumption test so they describe first-user dogfooding, small product-building teams, and the optional flywheel boundary.

I finished by running `uv run oe validate product`, `uv run oe tree product`, `uv run oe list icps --root product`, and a stale-reference scan with `rg -n "TODO|icp\\.solo-software-product-builders|solo-software-product-builders|Solo software product builders" product`.

### Why

The audit identified a real mismatch: the graph said the strategy focused on solo builders while one branch served small founder teams, and the vision carried too much current strategy and delivery mechanism. The user clarified that the real first user is the product builder, that the ICP should intentionally include small founder/product-building teams, and that the flywheel is desired but should not become required for normal graph usage.

### What worked

Using `oe new` for the assumption test placed it under the correct solution and preserved graph structure. The final `uv run oe validate product` passed, and `uv run oe tree product` showed the new assumption test under `solution.hosted-read-only-product-graph`. `uv run oe list icps --root product` resolved the renamed ICP as `icp.small-product-building-teams`.

### What didn't work

The generated assumption-test marker included the default TODO template after the filled-out content. I caught this with `sed -n '1,220p' product/outcomes/first-committed-practitioners/opportunities/everyone-sees-same-product-direction/solutions/hosted-read-only-product-graph/assumption-tests/hosted-read-only-graph-repeated-alignment-value/ASSUMPTION_TEST.md` and removed the duplicate TODO block. The final stale-reference scan returned no matches.

### What I learned

The graph is intentionally in a dogfooding stage. Lack of external evidence is not itself the highest-risk problem yet; the more important discipline is being explicit that early evidence comes from first-user use while shaping an MVP that can later convince other small builders and teams.

### What was tricky

Renaming the ICP was more than a label change because outcomes reference ICP ids. The content also needed to distinguish two related truths: the flywheel is a valid first-user need, and the core graph must remain usable without flywheel concepts.

### What warrants review

Review `/product/STRATEGY.md` to confirm the expanded ICP and first-user framing match the intended wedge. Review `/product/VISION.md` to confirm it now feels durable rather than too abstract. Review the new assumption test to decide whether the hosted read-only graph test should use the Outcome Engineering MVP workflow first, or whether it needs an external participant earlier.

### Future work

The hosted graph branch now has a value assumption test, but the graph still needs actual evidence once the MVP exists. The flywheel branch should stay optional until first-user use or early adopter feedback proves it changes real strategy decisions.

## Step 2: Restore solo builders as a distinct ICP

**Author:** main

### Prompt Context

**Verbatim prompt:** Okay just some feedback. I see the ICP thing you made so I would not want you to make a new ICP. You should still keep the old one but they just introduced a new one so we are having two ICPs:
- solo builder because there's a lot of them
- the small team because that's basically me and what I'm trying to do
Strategically the small founder and all of the small solo builders is a way bigger market and easier to actually inspire to use this thing so we need to keep two ICPs and

**Interpretation:** The previous PR update incorrectly replaced the solo-builder ICP with the small-team ICP. The graph should instead keep both ICPs, with solo builders as the broader adoption market and small teams as the first-user/founder-team context.

**Inferred intent:** Preserve strategic segmentation instead of collapsing distinct early markets into one ICP.

### What I did

I restored `/product/icps/solo-software-product-builders/ICP.md` as a separate ICP and kept `/product/icps/small-product-building-teams/ICP.md`. I updated `/product/STRATEGY.md` to explicitly describe the two-ICP wedge and why each matters. I updated `/product/outcomes/first-committed-practitioners/OUTCOME.md` and `/product/outcomes/builders-understand-strategy-flywheel/OUTCOME.md` so both outcomes reference both ICP ids.

### Why

Solo builders and small founder/product-building teams have overlapping pains but different adoption logic. Solo builders are a larger and easier-to-inspire market. Small teams represent the current dogfooding context and introduce shared-direction needs.

### What worked

Restoring the ICP as a separate node kept the graph model clean: ICPs remain top-level nodes, and outcomes can reference both.

### What didn't work

The previous edit treated the ICP expansion as a replacement rather than an addition. That lost an important strategic segment and created the wrong product story.

### What I learned

When an ICP broadens, it may need to become multiple ICPs rather than one umbrella. The graph should preserve strategically meaningful segmentation even when pains overlap.

### What was tricky

The small-team ICP originally included solo builders in its description, which blurred the distinction. I added language clarifying that the small-team ICP is specifically about shared direction across a founder, collaborator, or teammate.

### What warrants review

Review the strategy language to confirm the two-ICP wedge is now correct. Also review whether the flywheel outcome should serve both ICPs or only the small-team/first-user ICP.

### Future work

If the two ICPs diverge further, future outcomes may need to reference only one ICP rather than both.
