# Diary: ICPs as a top-level reference collection

This adds the ICP (ideal customer profile) concept to the framework. A graph can hold one or more ICPs in a top-level `icps/` collection, and outcomes and opportunities reference the ICPs they serve by id rather than nesting under them.

## Step 1: Place ICPs in the graph

**Author:** main

### Prompt Context

**Verbatim prompt:** "I feel like the concept of an ICP is missing from the framework. A graph should be able to have one or more ICPs. Where do you think it would fit in, into the graph?" followed by "I love your suggestion, please build it".

**Interpretation:** Decide where ICPs belong in the product graph, then implement that placement across the model, CLI, example, docs, and tests.

**Inferred intent:** Make "who the graph serves" a first-class, traceable part of the graph without breaking the outcome → opportunity → solution trace chain.

### What I did

I modeled an ICP as a "who," not a "do." An ICP is not a step in the causal trace chain, so it does not nest under another node. Instead ICPs live in a top-level `product/icps/` collection (kind `icp`, marker `ICP.md`), and outcomes and opportunities point at them by id through an `icps:` field in their yaml block. This keeps the many-to-many reality — one ICP serves many outcomes, one outcome serves many ICPs — that strict tree nesting would break.

In `/src/outcome_engineering/model.py` I added the `ICP.md` marker, the `icps` collection, the `ICP_REFERENCE_FIELD`, the kinds allowed to reference ICPs (`outcome`, `opportunity`), and a `ROOT_KINDS` set so `outcome` and `icp` share the "lives at the graph root" rule.

In `/src/outcome_engineering/graph.py` I taught `discover_nodes` to find the `icps/` collection, generalized `create_node` so any root kind works without `--under`, added an `icp` template, and added a tiny yaml-block parser (`parse_icp_references`, no new dependency) plus `node_icp_references`, `resolve_icp_references`, and `related_icps`. Validation now checks that ICP markers only appear directly under `icps/`, that ICP references resolve to known ICP ids, and that only outcomes and opportunities declare them.

In `/src/outcome_engineering/cli.py` the `oe context` command now resolves a node's ICPs — including ones inherited from outcome or opportunity ancestors — and prints them with their content, so agents see who the work serves. `oe new icp`, `oe list icps`, and `oe tree` work without command-specific edits because the model centralizes the rules.

I added an `icp.solo-knowledge-worker` ICP to the generated example and referenced it from the example outcome, added a real `icp.agent-native-builder` to `/product` referenced from `outcome.messy-product-assumptions`, updated the `oe-cli` and `challenge-product-intent` skills (both copies), the README, and `/tests/test_graph.py`.

### Why

ICPs are referenced from many nodes the way strategy is not, and an outcome can legitimately serve several ICPs. A reference collection captures that cleanly; a new layer in the trace chain would have forced a false 1:1 and broken the "each layer is the next reasoning step" property.

### What worked

Centralizing the rules in the model meant create, validate, discover, list, tree, and `new` picked up the `icp` kind without per-command changes. `uv run pytest` (21 passed), `uv run oe create-example --force`, `uv run oe validate product`, `uv run oe tree product`, and `uv run oe context` all passed, and context correctly inherited the outcome's ICP down to a deep solution node.

### What didn't work

No command failed.

### What I learned

Inheritance is the feature that makes references pay off: a solution deep in the tree never declares an ICP, but `related_icps` walks its ancestors so `oe context` still shows who it serves.

### What was tricky

ICPs sit at the root like `VISION.md` and `STRATEGY.md` but are a collection like `outcomes/`, so they needed their own discovery and validation path rather than reusing the trace-relationship machinery — folding `icps` into `RELATIONSHIP_TO_CHILD_KIND` would have made them nestable as trace children, which is exactly what the design avoids. The bundled skills still exist in two byte-identical copies that were updated together.

### What warrants review

Review `/src/outcome_engineering/model.py` and `/src/outcome_engineering/graph.py` for whether the reference-not-nest placement and the outcome/opportunity-only referencing rule match intent. Validate with `uv run pytest` and `uv run oe validate product`.

### Future work

Consider whether solutions should be allowed to reference ICPs (today only outcomes and opportunities can), whether ICPs warrant their own challenge skill ("which ICP does this serve, and is it the right one?"), and whether the visual graph UI should render ICPs as a distinct band rather than inline at the top of the tree.
