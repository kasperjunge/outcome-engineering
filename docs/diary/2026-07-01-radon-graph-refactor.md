# Diary: radon graph refactor

Refactored the Outcome Engineering Python package using Radon output, with `graph.py` as the main target because it had grown to 729 lines and contained the highest-complexity validation logic.

## Step 1: Split graph parsing and validation

**Author:** main

### Prompt Context

**Verbatim prompt:** Please run the python code analysis tool radon in the outcome-engineering source code and use it to refactor the codebase. As an example the graph.py file is getting really long (730 lines of code).
**Interpretation:** Run Radon against the source package, use its complexity and size findings to refactor the codebase, and specifically address the oversized `/src/outcome_engineering/graph.py`.
**Inferred intent:** Reduce concentrated complexity and file size without changing graph behavior or the CLI/API contracts that existing tests exercise.

### What I did

I created the `/Users/kasperjunge/Agent/Code/kasperjunge/private/outcome-engineering/.worktrees/radon-graph-refactor` worktree from `main` and ran Radon with `uv run --with radon radon cc src/outcome_engineering -s -a`, `uv run --with radon radon mi src/outcome_engineering -s`, and `uv run --with radon radon raw src/outcome_engineering`. The first direct command, `uv run radon cc src/outcome_engineering -s -a`, failed because Radon was not installed in the project environment.

Radon identified `/src/outcome_engineering/graph.py` as the hotspot: 729 LOC, maintainability index `C (0.00)`, and `/src/outcome_engineering/graph.py:466 validate` at `F (52)`. I extracted frontmatter parsing into `/src/outcome_engineering/frontmatter.py` and validation into `/src/outcome_engineering/validation.py`, then left compatibility imports in `/src/outcome_engineering/graph.py` so existing imports from `outcome_engineering.graph` still work. I also split flywheel discovery helpers in `/src/outcome_engineering/graph.py` and payload/context assembly helpers in `/src/outcome_engineering/read.py` to remove remaining `C`-grade functions found in the second Radon pass.

### Why

The original `/src/outcome_engineering/graph.py` mixed graph traversal, mutation, frontmatter parsing, and validation. Moving parsing and validation into focused modules made the file smaller and made the high-complexity validation path easier to inspect and test independently.

### What worked

The existing `/tests/test_graph.py` suite covered the validation behavior well enough to make the extraction low-risk. After the refactor, `uv run ruff check src tests` passed and `uv run pytest` reported 56 passing tests.

### What didn't work

`uv run radon cc src/outcome_engineering -s -a` failed with `error: Failed to spawn: \`radon\`` and `Caused by: No such file or directory (os error 2)` because Radon is not a project dependency. Running it as `uv run --with radon radon ...` worked without adding a dependency.

### What I learned

`graph.py` had one severe hotspot rather than broad complexity across the package. Once `validate()` moved into phased helpers, the worst remaining source functions were all `B` grade, and `/src/outcome_engineering/read.py` had two straightforward assembly functions that could be decomposed without changing output shape.

### What was tricky

The main compatibility concern was import stability. Existing callers import parsing helpers and `validate` from `outcome_engineering.graph`, so `/src/outcome_engineering/graph.py` now re-exports moved functions from the new modules.

### What warrants review

Review `/src/outcome_engineering/validation.py` for whether the phase boundaries read naturally and `/src/outcome_engineering/graph.py` for whether the compatibility imports are explicit enough. Validate with `uv run pytest`, `uv run ruff check src tests`, and `uv run --with radon radon cc src/outcome_engineering -s -a`.

### Future work

`/src/outcome_engineering/validation.py` is now the largest logic module introduced by the split. It is much lower complexity than the original `validate()` function, but future validation features should keep extending the phase helpers rather than accumulating new branches in one function.

## Step 2: Remove bundled example generator and extract node templates

**Author:** main

### Prompt Context

**Verbatim prompt:** remove that
**Interpretation:** Remove the production `example.py` generator that creates bundled example graphs.
**Inferred intent:** Keep the package focused on product graph tooling rather than shipping a large embedded example data generator.

### What I did

I removed `/src/outcome_engineering/example.py`, deleted `/scripts/create_example_product_graph.py`, removed the `oe create-example` CLI command from `/src/outcome_engineering/cli.py`, and removed create-example references from `/README.md` and `/src/outcome_engineering/skills/oe-cli/SKILL.md`. I replaced test usage of the production generator with a compact local `create_sample_graph` helper in `/tests/test_graph.py` and removed tests that only covered the deleted comprehensive and Boligsiden generators.

After the follow-up prompt asking to factor out `render_template`, I added `/src/outcome_engineering/node_templates.py`, moved each node template into `/src/outcome_engineering/templates/nodes/*.md.j2`, and added `jinja2` as a direct runtime dependency in `/pyproject.toml`.

### Why

The large generator was mostly embedded example data and made the package look more complex than the core graph tooling. The inline template dictionary in `/src/outcome_engineering/graph.py` had similar pressure: editing templates required editing graph logic.

### What worked

Removing the generator dropped the test suite to the behavior-focused tests that still exercise validation, graph payloads, serving, hosted reads, and node creation. The new Jinja templates keep the Markdown scaffolds visible as individual files and make `/src/outcome_engineering/graph.py` smaller.

### What didn't work

No command failed in this step. `uv sync` added `jinja2==3.1.6` and `markupsafe==3.0.3` to the lockfile.

### What I learned

Most tests did not need the large example generator; they only depended on a few stable node ids. A small test-local graph fixture was enough for those cases.

### What was tricky

The main risk was deleting a production module that tests imported heavily. Replacing it with a local fixture avoided keeping a fake production example API solely for tests.

### What warrants review

Review `/src/outcome_engineering/templates/nodes/` for whether the default node scaffolds still match the intended product graph authoring flow. Review `/tests/test_graph.py` to confirm the smaller fixture still covers the right graph shapes.

### Future work

If examples are still useful, keep them as checked-in graph directories under `/examples` or docs, not as a Python generator embedded in the package.

## Step 3: Introduce core graph interface and module boundaries

**Author:** main

### Prompt Context

**Verbatim prompt:** please refactor the modules of the src/outcome_engineering . Improve the design of the code to make it more well organized, decoupled, modularized and nice. Make it great great design until you're satisfied. Also, the core funtionality of the graph should be in one core interface, that stuff like cli, mcp, api, etc can plug into as needed (not all of them is implemented now, but to create easy optionality in the future). Think about the organization of th modules from first principles and good software design. i know yuo can do this. Keep going until you're statisfied.
**Interpretation:** Continue the refactor beyond file-size cleanup by designing a clearer module architecture and a central graph facade for CLI, API, and future integrations.
**Inferred intent:** Make the package easier to extend without coupling every surface directly to filesystem traversal, validation internals, and mutation helpers.

### What I did

I added `/src/outcome_engineering/core.py` with the `ProductGraph` facade and `NodeResolutionError`. `ProductGraph` now owns the main integration surface: validation, node discovery, selector matching and resolution, flywheel access, ancestor traversal, ICP/supporting-file lookup, and graph mutations.

I split the low-level graph implementation into `/src/outcome_engineering/discovery.py` for filesystem discovery and read-only traversal, and `/src/outcome_engineering/mutations.py` for create/edit/delete operations. I turned `/src/outcome_engineering/graph.py` into a compatibility re-export module so existing imports continue to work while new code can depend on the clearer modules.

I updated `/src/outcome_engineering/validation.py` to depend directly on discovery helpers instead of lazy-importing from `graph.py`. I updated `/src/outcome_engineering/read.py`, `/src/outcome_engineering/cli.py`, `/src/outcome_engineering/serve.py`, and `/src/outcome_engineering/hosted.py` so the application surfaces route graph operations through `ProductGraph`. I also exported `ProductGraph` and `NodeResolutionError` from `/src/outcome_engineering/__init__.py`.

### Why

The previous module shape had improved internals, but callers still composed low-level functions directly. A central `ProductGraph` interface makes the architecture explicit: core graph behavior lives behind one facade, and adapters such as CLI commands, editable HTTP handlers, hosted read APIs, or a future MCP server can plug into that facade.

### What worked

The compatibility shim let the existing test imports remain stable while the implementation moved underneath. After the refactor, `uv run ruff check src tests`, `uv run pytest`, `uv run oe validate product`, `uv build`, and Radon all passed.

### What didn't work

No verification command failed during this step. Ruff did catch that `NodeResolutionError` needed an explicit re-export in `/src/outcome_engineering/read.py`; I fixed that with an alias import.

### What I learned

The cleanest boundary is: `model.py` defines rules and data, `discovery.py` reads the filesystem graph, `mutations.py` changes it, `validation.py` checks it, `core.py` coordinates it, `read.py` presents read payloads, and `cli.py` / `serve.py` / `hosted.py` are adapters.

### What was tricky

The main tension was preserving backwards compatibility while creating a better forward path. Keeping `/src/outcome_engineering/graph.py` as a re-export layer avoids a breaking import churn while making `ProductGraph` the preferred integration point.

### What warrants review

Review `/src/outcome_engineering/core.py` as the new interface contract. Then review `/src/outcome_engineering/discovery.py` and `/src/outcome_engineering/mutations.py` to confirm the boundary between reads and writes feels right. Validate with `uv run pytest`, `uv run ruff check src tests`, `uv run oe validate product`, and `uv build`.

### Future work

Future integrations should start from `ProductGraph`. If the read payload API grows, consider moving payload construction from `/src/outcome_engineering/read.py` into a dedicated adapter package rather than adding more responsibilities to `core.py`.

## Step 4: Replace flat modules with packages and structure hosted FastAPI

**Author:** main

### Prompt Context

**Verbatim prompt:** the module structure is flat, which makes it not very easy to get an overview. also the fastapi app is should be structure like following best practices for fastapi apps. right now everything is just in hosted.py - lay the foundation for a proper well structured and written fastapi app. Also look for other opportuninties to make the src/outcome_engieering more clean. Keep going until you're satisfied.
**Interpretation:** Continue the architecture refactor by replacing the flat module layout with clearer packages, and split the hosted FastAPI app out of one file into a maintainable app structure.
**Inferred intent:** Make the package easier to scan and extend by grouping domain logic, read projections, hosted API code, and local UI serving code by responsibility.

### What I did

I moved the graph domain implementation into `/src/outcome_engineering/product_graph/`, including `/core.py`, `/discovery.py`, `/frontmatter.py`, `/model.py`, `/mutations.py`, `/node_templates.py`, `/read.py`, and `/validation.py`. I kept thin compatibility shims at the old top-level module names so existing imports like `outcome_engineering.graph`, `outcome_engineering.read`, and `outcome_engineering.model` still resolve.

I replaced the flat `/src/outcome_engineering/hosted.py` module with a `/src/outcome_engineering/hosted/` package. The new structure separates `/hosted/app.py` for the app factory, `/hosted/dependencies.py` for request-scoped graph access, `/hosted/errors.py` for HTTP error translation, `/hosted/web.py` for the HTML route, and `/hosted/api/` for graph and validation routers. The existing `outcome_engineering.hosted:app` and `create_app` import path still works through `/hosted/__init__.py`.

I also moved the editable stdlib web server into `/src/outcome_engineering/local_ui/server.py` and left `/src/outcome_engineering/serve.py` as a compatibility shim.

### Why

The previous refactor improved module responsibilities, but the files were still listed as a flat set at package root. Grouping by domain and adapter makes the top-level overview clearer: `product_graph/` is the core graph package, `hosted/` is the FastAPI app, and `local_ui/` is the local editable UI server.

### What worked

The compatibility shims allowed the package to preserve current public imports while moving the implementation into clearer packages. `uv run ruff check src tests`, `uv run pytest`, import checks for old and new paths, `uv run oe validate product`, `uv build`, and Radon all passed.

### What didn't work

Ruff caught that `/src/outcome_engineering/serve.py` initially relied on a star import while naming `__all__`, so I changed it to explicit imports from `/src/outcome_engineering/local_ui/server.py`.

### What I learned

The hosted app was small enough that a heavy service layer would be unnecessary, but it still benefits from the conventional FastAPI split: app factory, dependencies, routers, and error helpers. The local editable UI should remain separate from the hosted read-only FastAPI app because their runtime concerns are different.

### What was tricky

The biggest risk was the namespace transition from a single `/hosted.py` file to a `/hosted/` package. Keeping `/hosted/__init__.py` as the public export point preserved the documented `uvicorn outcome_engineering.hosted:app` entry point.

### What warrants review

Review `/src/outcome_engineering/product_graph/` for the domain package boundary, `/src/outcome_engineering/hosted/` for the FastAPI structure, and `/src/outcome_engineering/local_ui/server.py` for the separation from hosted read-only serving.

### Future work

If the CLI grows, it should get the same treatment as hosted: a small package with command groups and shared CLI error handling instead of one module.

## Step 5: Remove stale flat compatibility shims

**Author:** main

### Prompt Context

**Verbatim prompt:** you forgot to clean up a lot of files it seems?
**Interpretation:** The previous pass left stale-looking flat compatibility modules and generated cache/build files that made the package still look cluttered.
**Inferred intent:** Finish the cleanup so the repository tree reflects the new package structure clearly, not just internally.

### What I did

I removed the one-line top-level compatibility shims for `/core.py`, `/discovery.py`, `/frontmatter.py`, `/graph.py`, `/model.py`, `/mutations.py`, `/node_templates.py`, `/read.py`, `/serve.py`, and `/validation.py`. I updated `/tests/test_graph.py` to import from `/product_graph/` and `/local_ui/` directly. I also removed generated `dist/`, `__pycache__/`, and `.pyc` files created by verification commands.

### Why

The shims preserved old import paths, but they also kept the root package visually flat and undermined the goal of making the structure easier to understand at a glance.

### What worked

After removing the shims, `uv run ruff check src tests`, `uv run pytest`, `uv run oe validate product`, `uv build`, and Radon all passed.

### What didn't work

`uv build` and test runs recreate generated files, so I had to remove `dist/` and `__pycache__/` again after verification.

### What I learned

Keeping compatibility shims is not always worth the visual and structural cost during a deliberate architecture cleanup. In this repo, direct imports from `product_graph`, `hosted`, and `local_ui` make the intended boundaries clearer.

### What was tricky

The only care point was making sure the test suite no longer depended on `outcome_engineering.graph` before deleting the shim.

### What warrants review

Review the root of `/src/outcome_engineering/`; it should now show only package entry points and adapter packages rather than duplicate flat graph modules.

### Future work

If external users need backwards compatibility for the old flat module imports, add an intentional deprecation plan rather than reintroducing silent shims.
