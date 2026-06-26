# Diary: Agent entry point docs

This captures the docs update that aligns the repository copy with the new product vision and strategy.

## Step 1: Reframe docs around first useful jobs

**Author:** main

### Prompt Context

**Verbatim prompt:** "do it"
**Interpretation:** Update the repository docs and copy to make them more effective toward the newly added Outcome Engineering vision and strategy.
**Inferred intent:** Make the README and docs lead with the agent-native strategic entry points instead of requiring readers to understand the whole framework first.

### What I did

I rewrote the opening of `/README.md` around the vision sentence, the three strategic jobs, and the "start small" principle. I added `/docs/agent-entry-points.md` to describe challenge assumptions, craft vision and strategy, and challenge product intent as the first agent-native use cases. I validated the root product graph with `uv run oe validate product`.

### Why

The existing docs explained the framework well, but they led with abstract traceability and the full conceptual model. The new strategy says Outcome Engineering should be useful from messy entry points first, then grow a coherent graph around the work.

### What worked

The README could be repositioned without removing the core framework explanation. The new entry-points doc gives agents and humans a concise bridge from messy product material to graph-backed product memory.

### What didn't work

Nothing broke. The validation command was:

```sh
uv run oe validate product
```

It returned:

```text
OK: product is a valid product graph
```

### What I learned

The clearest external copy starts with what Outcome Engineering helps users do: challenge assumptions, craft vision and strategy, and challenge product intent. The graph matters most when presented as durable memory behind those jobs.

### What was tricky

The main constraint was keeping the README direct while preserving enough of the original framework explanation for readers who want the deeper model.

### What warrants review

Review `/README.md` for whether the opening now sells the method clearly enough. Review `/docs/agent-entry-points.md` for whether the three entry points are concrete enough to guide future agent skills.

### Future work

The next likely docs improvement is to turn each entry point into a concrete skill or prompt flow once the desired interaction pattern is clearer.
