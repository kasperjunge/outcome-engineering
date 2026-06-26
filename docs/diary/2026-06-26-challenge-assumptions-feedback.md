# Diary: Challenge Assumptions Feedback

This records what changed after using the `challenge-assumptions` skill on its own product graph and getting immediate user feedback about the interaction model.

## Step 1: Recenter challenge-assumptions on the user's input

**Author:** main

### Prompt Context

**Verbatim prompt:** the user does not care about the graph so dont mention it as if it was the central thing.


Please try to make thoese changes and reinstall skill

**Interpretation:** The `challenge-assumptions` skill was making the product graph too visible in the user-facing response. The user wanted the skill to listen first for the thing to challenge, use the graph as background context, and reinstall the updated skill.

**Inferred intent:** The skill should feel like a product judgment tool, not a graph inspection tool. The product graph should provide structure and memory behind the scenes without becoming the center of the conversation.

### What I did

I updated `/skills/challenge-assumptions/SKILL.md` and `/src/outcome_engineering/skills/challenge-assumptions/SKILL.md`. The new wording tells the agent to first listen for an idea, feature, PRD, assumption, solution, opportunity, or messy pasted notes. If the user has not provided anything to challenge, the skill now says to ask for it directly and stop instead of inspecting or explaining graph structure.

I kept the `oe-cli` workflow, but reframed it as quiet background work. The skill now explicitly says not to narrate graph validation, tree structure, node ids, or CLI steps unless the user asks. It also says to mention the graph only when it materially changes the product judgment or when suggesting a concrete edit.

I reinstalled the active agent skills with:

```sh
uv run oe install --skills=agents --force
```

That refreshed `/.agents/skills/challenge-assumptions/SKILL.md` along with the other bundled agent skills. I then verified the installed skill content with:

```sh
sed -n '1,220p' .agents/skills/challenge-assumptions/SKILL.md
```

I also validated the product graph with:

```sh
uv run oe validate product
```

### Why

The live use exposed a mismatch between the method and the experience. The graph is useful for grounding and traceability, but the user is asking for help challenging product thinking. Leading with graph validation and tree details made the internal mechanism feel like the product.

### What worked

The source skill, packaged skill, and installed skill all had the same simple structure, so the change was easy to make consistently. The installer path worked cleanly and confirmed that the active `.agents` skill was regenerated from the packaged skill.

### What didn't work

During the initial live use of the skill, I ran:

```sh
test -d product && uv run oe validate product; status=$?; exit $status
```

That produced:

```text
OK: product is a valid product graph
zsh:1: read-only variable: status
```

The validation itself succeeded, but `status` is a read-only variable in zsh, so that command shape is brittle. Use a different variable name or avoid assigning the exit code that way.

The bigger product failure was that I surfaced too much process. I told the user the graph validated, described its minimal shape, and anchored the response around graph context. That was technically correct but experientially wrong for this skill.

### What I learned

For this workflow, the graph should behave like product memory, not like the conversational subject. The user wants their idea challenged. The skill should only expose graph details if they improve the challenge, reveal an important conflict, or support a proposed edit.

The first response from `challenge-assumptions` should usually be either a direct challenge of the user's supplied product thinking or a short request for the thing to challenge. It should not start by reporting repository state.

The output order matters. Putting graph suggestions after the next learning step reinforces that graph edits are secondary to learning.

### What was tricky

The skill still needs to use `oe-cli` when a graph is present, because that is how Outcome Engineering keeps product intent durable and traceable. The tricky part is separating agent behavior from user-facing narration: use the graph internally, but do not make the user watch the scaffolding.

There are multiple copies of the skill: `/skills/challenge-assumptions/SKILL.md`, `/src/outcome_engineering/skills/challenge-assumptions/SKILL.md`, and the installed `/.agents/skills/challenge-assumptions/SKILL.md`. The packaged copy under `/src/outcome_engineering/skills/` is what the installer uses, so it must stay in sync with the repo-level skill copy.

### What warrants review

Review `/skills/challenge-assumptions/SKILL.md` and `/src/outcome_engineering/skills/challenge-assumptions/SKILL.md` for whether the wording is strong enough to suppress graph narration in future runs.

Validate behavior by invoking `$challenge-assumptions` without a product idea. The expected response should be a concise request for the idea or messy notes to challenge, not a report about graph validation or graph shape.

Then validate with a real messy product idea. The expected response should lead with hidden assumptions, the riskiest assumption, and a learning step. Graph edits should appear only if they are genuinely useful.

### Future work

The other strategic skills may need the same interaction principle: use the graph as background structure, but keep the user's product question in the foreground. In particular, `challenge-product-intent` should probably avoid presenting trace mechanics unless the trace reveals a meaningful product issue.

Future installer tests could assert that the packaged skills and repo-level skills stay synchronized, because manual drift across `/skills/` and `/src/outcome_engineering/skills/` would be easy to miss.

## Step 2: Capture the lesson in the diary

**Author:** main

### Prompt Context

**Verbatim prompt:** write down what you learned in a diary

**Interpretation:** Add a diary entry documenting the feedback loop, implementation change, reinstall command, validation, and product lesson from the `challenge-assumptions` update.

**Inferred intent:** Preserve the tacit lesson from the live skill use so future work on Outcome Engineering skills does not repeat the same user-experience mistake.

### What I did

I created `/docs/diary/2026-06-26-challenge-assumptions-feedback.md` with the implementation narrative, commands, validation notes, and the key behavioral lesson.

### Why

The feedback was not just a wording tweak. It clarified the intended relationship between the graph, the agent, and the user: graph-aware but not graph-centered.

### What worked

The diary format gave a clear place to record both the technical change and the interaction lesson. The current repository already had `/docs/diary/`, so the new entry fit the existing documentation pattern.

### What didn't work

Nothing failed during the diary write itself.

### What I learned

Diary entries are useful for preserving product interaction lessons, not only code-level implementation details. This is especially useful for skills, where small wording choices strongly shape future agent behavior.

### What was tricky

The diary needed to capture the user's feedback accurately without overexplaining the graph again. The important lesson is concise: the graph is background context, while the user's product thinking is the foreground.

### What warrants review

Check whether this diary should later be linked from the broader strategic skills diary if that becomes an index of skill behavior lessons.

### Future work

Use this diary when revising the other agent skills so they keep their internal graph work separate from the user-facing product conversation.
