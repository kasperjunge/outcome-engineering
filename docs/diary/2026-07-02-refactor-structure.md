# Diary: Restructure src around the ProductGraph facade

Refactor the `outcome_engineering` package to fix the structural issues found in a code review (facade bypass, duplicated selector matching, duplicated payload builders, mixed concerns in `read.py`, env-var config in the core, repeated filesystem walks) plus the conclusions of a design-pattern analysis (complete the Facade; validators as a Strategy-style tuple; reject other patterns).

## Step 1: Implement the full refactor

**Author:** main

### Prompt Context

**Verbatim prompt:** "improve the codebase with all the stuff we just talkeb about" (via `/goal`)
**Interpretation:** Implement all six review fixes and the pattern-analysis conclusions from the preceding conversation, in a worktree per workspace rules.
**Inferred intent:** Make the codebase's stated architecture (everything depends on the `ProductGraph` facade) actually true, and remove duplication before it drifts.

### What I did

Worked in `.worktrees/refactor-structure` on branch `refactor-structure`, commit `305366b`.

- `/src/outcome_engineering/product_graph/discovery.py`: added `match_nodes(nodes, selector)` as the single selector matcher (pure filter); `matching_nodes(root, ...)` and `find_node` derive from it.
- `/src/outcome_engineering/product_graph/core.py`: facade now caches `discover_nodes` per instance (`_nodes_cache`, invalidated by `create_node`/`write_marker`/`delete_node`), gains `context(selector)` and `kinds()`, and `find`/`matching`/`resolve`/`find_by_kind` all run off the cached node list via `match_nodes`.
- `/src/outcome_engineering/product_graph/read.py`: rewritten — all functions take a `ProductGraph` instance instead of a `Path`; `node_payload` is the one payload builder (`build_graph_payload` adds `deletable`, `node_summary` is a key subset via `SUMMARY_KEYS`); deleted `title_from_body`, `resolve_node`, `matching_nodes` wrappers and `SourceMetadata`; imports `core` only under `TYPE_CHECKING` so `core → read` is the single runtime direction.
- `/src/outcome_engineering/product_graph/render.py`: new — `context_markdown` and the `_append_*` helpers moved out of `read.py`.
- `/src/outcome_engineering/product_graph/validation.py`: rules normalized to a uniform `(root, graph_dirs, context)` signature and run from a `VALIDATORS` tuple. Also fixed a latent bug: `_validate_strategy_periods_do_not_overlap` enumerated the *sorted* period list but sliced the *original* list, so out-of-order files could self-compare or skip pairs.
- `/src/outcome_engineering/hosted/source.py`: new home for `SourceMetadata`; branch default changed from `"main"` to `"unknown"`. Hosted routes (`api/graph.py`, `api/validation.py`) now take the `ProductGraph` dependency and append `source` themselves; `errors.py` operates on graphs.
- `/src/outcome_engineering/local_ui/server.py`: dropped the `_issues` alias; handlers pass `self._graph()` into `build_graph_payload`/`issue_dicts`.
- `/src/outcome_engineering/cli.py`: imports only the facade (`ProductGraph`, `NodeResolutionError`); `context` command uses `graph.context()`; kind validation uses `ProductGraph.kinds()`.
- `/tests/test_graph.py`: updated call sites to pass `ProductGraph(root)`, moved the source-metadata assertion to the hosted test (`branch == "unknown"`), added a cache-invalidation test. 53 tests pass; ruff clean.

### Why

The review found the facade was documented as mandatory but bypassed by its own siblings and clients, and the pattern analysis confirmed "complete the Facade" as the only structural change worth making. Injecting the graph into `read.py` kills the reverse dependency and makes the discovery cache actually effective (previously `resolve` could walk the filesystem three times).

### What worked

Doing the dedup steps (matcher, payloads) before the facade completion made the later edits small, as predicted. The existing test suite was dense enough to catch every signature change immediately.

### What didn't work

Two self-inflicted stumbles, both caught before landing: (1) first draft of `core.matching` called the root-based `matching_nodes`, silently bypassing the new cache — fixed by splitting out the pure `match_nodes` filter; (2) placed the `VALIDATORS` tuple above the function definitions, which would `NameError` at import — moved to end of module. Test run after the rewrite failed with `AttributeError: 'PosixPath' object has no attribute 'nodes'` in four tests still passing `root` paths; expected, fixed by updating call sites.

### What I learned

`read.py` needed no runtime import from `core` at all — `from __future__ import annotations` plus a `TYPE_CHECKING` block was enough to keep type hints while making the dependency direction strictly `core → read`. Also, frozen dataclasses can hold a mutable cache cleanly via `field(init=False, compare=False)` + `object.__setattr__`.

### What was tricky

The cache/matcher interaction: the "single source of truth" matcher originally took a root and re-walked the filesystem, which conflicted with per-instance caching. The resolution was making the matcher a pure function over an already-discovered node list.

### What warrants review

- JSON shape changes: direct `read.py` outputs no longer include `source` (hosted routes add it), and hosted `branch`/`commit` now default to `"unknown"` instead of `"main"`. Anything consuming the hosted API's `source.branch` default should be checked.
- The overlap-validation bug fix in `/src/outcome_engineering/product_graph/validation.py` changes which issues are reported for out-of-order strategy files — intended, but it is a behavior change without a dedicated regression test.
- Cache staleness: a `ProductGraph` instance won't see filesystem changes made behind its back. Both servers construct per-request instances so this is safe today; documented in the facade docstring.

### Future work

- A regression test for the strategy-period overlap fix with deliberately unsorted file order.
- `validate()` still re-walks independently of the node cache; could share discovery if graphs grow.
- Merge branch, remove the worktree, and delete the branch per workspace worktree rules.
