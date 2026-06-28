# Diary: OE Grill skill

This records the strategy shift toward the visual product graph and the first conversational skill for building that graph from messy product thinking.

## Step 1: Add consultant skill and update strategy

**Author:** main

### Prompt Context

**Verbatim prompt:** "This skill should basically be a skill that you activate when you want to just talk about your product and how it's going and stuff like that. The agent should use that as a way to learn about the thoughts of the author and suggest updates and whatever. Great, make that skill. We will iterate on it but also change the strategy. I don't think the vision needs any changing but we need to change the strategy towords this"
**Interpretation:** Create a new Outcome Engineering skill for conversational product graph consulting, and rewrite the strategy away from the older three skill-shaped directions toward framework teaching, visual graph editing, and agent-legible graph usage.
**Inferred intent:** Make the product direction and bundled skill surface match the emerging strategy: the graph is the main product object, the visual editor is the adoption surface, and agents help maintain product understanding through the graph.

### What I did

I added `/skills/oe-grill/SKILL.md` and the packaged copy at `/src/outcome_engineering/skills/oe-grill/SKILL.md`. The skill instructs agents to act as conversational product consultants, start from whatever the user brings, map product thinking into the Outcome Engineering graph, ask one question at a time, explain intended graph edits before making them, and use `oe` for graph inspection and mutation.

I updated `/src/outcome_engineering/skill_installer.py` so bundled skill installation includes both `oe-cli` and `oe-grill`. I rewrote `/product/STRATEGY.md` so the strategic pillars are now teaching the framework, making the graph visually usable, and making the graph agent-legible.

### Why

The old strategy centered standalone challenge/craft/review skills. The new direction centers the product graph as the team artifact and the visual editor as the main product surface. The consultant skill gives agents an initial behavior for helping users turn live product conversations into durable graph updates.

### What worked

The existing installer already supported multiple bundled skills through `SKILL_NAMES`, so adding the new packaged skill required only extending that tuple. The strategy rewrite could keep the existing vision intact while changing the adoption wedge and pillars.

### What didn't work

No command failed during this step. The main friction was choosing a skill name broad enough to trigger for casual product conversations without losing the graph-specific behavior.

### What I learned

The repo intentionally removed earlier strategic skills, so the new skill should not recreate those as separate entry points. It should absorb those use cases as graph-centered conversation when they arise naturally.

### What was tricky

The skill needs to feel like "just talk about the product" while still being operationally useful. The guardrail is that every question should serve shared understanding or a potential graph update, and every edit should be small and explicit.

### What warrants review

Review `/skills/oe-grill/SKILL.md`, `/src/outcome_engineering/skills/oe-grill/SKILL.md`, and `/product/STRATEGY.md` for whether the wording captures the intended conversational consultant behavior. Validate that bundled skill installation still works and that the product graph remains valid.

### Future work

The skill likely needs iteration after real use. The visual editor strategy may also imply new product graph nodes for near-term UI work once the desired implementation focus is clearer.
