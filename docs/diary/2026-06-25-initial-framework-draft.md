# Diary: Initial framework draft

Created the first written version of the Outcome Engineering framework.

## Step 1: Draft framework structure

**Author:** main

### Prompt Context

**Verbatim prompt:** Okay. Please take that into account when you write the repo. give it a shot
**Interpretation:** Write the initial repository documentation for Outcome Engineering, incorporating the idea that evidence and learning happen throughout the product graph, not only after release.
**Inferred intent:** Establish a concrete first draft that can be reviewed and refined into the foundation of the framework.

### What I did

I created `/README.md`, `/docs/framework.md`, `/docs/graph.md`, and `/docs/glossary.md`. I also created an empty initial commit on `main`, pushed it, and opened the actual drafting work in the `/.worktrees/draft-framework` worktree branch because this repository lives under `Code/`.

### Why

The repo needed an initial written theory, not just an empty shell. The main conceptual requirement was to avoid modeling evidence as something that only arrives after release, and instead describe evidence as something that can attach to any product belief.

### What worked

The structure split cleanly into a README for the short public-facing argument, a framework document for the theory, a graph document for relationships, and a glossary for term definitions.

### What didn't work

The repository had no commits, so a normal worktree branch could not be created before any repository state existed. I created an empty initial commit with `git commit --allow-empty -m "Initial commit"` and pushed it before creating `.worktrees/draft-framework`.

### What I learned

The framework reads more accurately when evidence is described as distributed across the graph. The phrase "Every node in the product development graph is a belief until supported by evidence" became the organizing principle for that part of the theory.

### What was tricky

The first high-level graph still risked implying a delivery pipeline. I updated `/docs/graph.md` so the Mermaid graph includes `Any Product Belief` and shows evidence as something that can be produced or required by beliefs at multiple levels.

### What warrants review

Review `/README.md` for whether the core claim is sharp enough, and `/docs/graph.md` for whether the graph is conceptually right or too visually crowded.

### Future work

The next useful step is to decide whether the framework should introduce a formal artifact schema for nodes, edges, evidence, confidence, and ownership.
