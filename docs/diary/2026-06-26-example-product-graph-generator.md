# Diary: Example product graph generator

Created a first code artifact for exploring how Outcome Engineering could live in a repository.

## Step 1: Generate an example filesystem graph

**Author:** main

### Prompt Context

**Verbatim prompt:** Great I think we got some first suggestion here. Can you actually write some code? First of all this is, of course, in the Outcome Engineering repo. Could you write some Python code that actually creates just an example, just a semi-random example structure like this, right, just to make it possible for me to see it? That would be great. Please do that.

Next up I think we're going to create some code that can actually deterministically create this structure and also check it, a tool for the agent to check that there is consistency and it's a valid structure
**Interpretation:** Add Python code to create a concrete example product graph directory using the proposed canonical-file convention, so the structure can be inspected before building deterministic creation and validation tools.
**Inferred intent:** Turn the conversation about repo-native product graphs into something tangible that can be evaluated.

### What I did

I added `/scripts/create_example_product_graph.py`, which creates `/examples/delegation-product-graph`. The generated graph uses canonical marker files such as `OUTCOME.md`, `OPPORTUNITY.md`, `SOLUTION.md`, `ASSUMPTION.md`, `EXPERIMENT.md`, and `PRD.md`. Relationship directories such as `opportunities/`, `solutions/`, `assumptions/`, `experiments/`, and `prds/` define parent-child edges.

I also added `/docs/example-structure.md` and linked it from `/README.md`.

### Why

The framework needed a concrete filesystem example before designing stricter creation and validation tools. Seeing paths and files should make it easier to judge whether the convention feels natural.

### What worked

The canonical-file pattern mapped cleanly onto the product graph idea. A path like `/outcomes/delegation-confidence/opportunities/agents-lack-safe-access-to-tools/solutions/agent-central/prds/agent-central-mvp/PRD.md` is readable by both humans and agents.

### What didn't work

No command failed. I chose deterministic sample data rather than actual randomness because the example should be stable in git.

### What I learned

Relationship directories are useful because they remove ambiguity. The node type comes from the marker file, while the relationship directory explains the edge from the parent node.

### What was tricky

The main design tension is keeping the tree browseable while leaving room for graph-like cross-links later. This first pass only models primary parent-child relationships.

### What warrants review

Review `/examples/delegation-product-graph` and decide whether the tree feels natural to browse. The most important thing to inspect is whether nested opportunities and solution-owned assumptions/experiments feel right.

### Future work

Build deterministic creation and validation tooling that can check marker files, relationship directories, IDs, duplicate nodes, missing parents, and invalid child types.

