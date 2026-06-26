# Diary: Trace and new commands

Added deterministic graph navigation and creation commands to the Outcome Engineering CLI.

## Step 1: Add trace and new

**Author:** main

### Prompt Context

**Verbatim prompt:** That is great. Please build it
**Interpretation:** Implement the deterministic mechanics discussed immediately before this prompt: `oe trace` and `oe new`, while leaving non-deterministic `oe challenge` out of scope.
**Inferred intent:** Make the CLI useful for agents and humans to navigate and maintain the product graph without hand-rolling folders.

### What I did

I added `oe trace`, which locates a node by id, slug, node path, or marker file path and prints its parent chain, marker file, relationship, and children.

I added `oe new`, which creates graph nodes in the correct relationship folder using canonical marker files and starter templates. It supports outcomes, opportunities, solutions, assumptions, experiments, and PRDs. It enforces that experiments can only be created under assumptions.

I added tests for graph creation, parent-chain tracing, and rejection of experiments under solutions.

### Why

Agents need deterministic mechanics before they can safely use the product graph. `trace` lets an agent understand where work sits in the graph. `new` lets an agent create valid graph structure instead of guessing paths.

### What worked

`uv run pytest` passed. `uv run oe trace solution.agent-central --root examples/delegation-product-graph` printed the expected outcome/opportunity/solution chain. A fresh temporary graph created entirely through `oe new` validated successfully and printed correctly with `oe tree`.

### What didn't work

No command failed during the final verification. The main design decision was to keep challenge out of scope because it requires product judgment and should later be powered by agent context, not deterministic validation.

### What I learned

The creation API needs to know both the node kind and relationship folder. Keeping `KIND_TO_RELATIONSHIP` and `PARENT_KIND_TO_CHILD_KIND` explicit makes the rules clear and testable.

### What was tricky

Node lookup supports both ids and slugs. Slugs can become ambiguous later, so `find_node` only resolves slug selectors when there is exactly one match.

### What warrants review

Review the starter templates created by `oe new`; they are intentionally plain but may need stronger required sections before the format hardens.

### Future work

Add `oe context` to emit machine-readable context for an agent, and later use that context as the input to an agent-assisted `oe challenge` workflow.

