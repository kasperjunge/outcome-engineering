---
type: strategy
id: strategy.visual-graph-wedge
name: 0 to 1
starts: 2026-06-28
ends: 2026-09-30
---

# Strategy

Outcome Engineering should win first with two closely related ICPs: solo software product builders and small product-building teams. Both are using agents to build faster than they can reliably make product decisions.

The core strategic shape is to teach a practical framework for structuring product work, make that framework usable through a visual repo-native graph, and keep the underlying graph legible enough that agents can help builders clarify, test, build, review, and act on product intent.

These builders should not need to understand the whole framework before receiving value. They should be able to start with whatever is on their mind, talk it through, see where it fits in the graph, and leave with clearer product judgment plus durable repo-native product memory.

The 0 to 1 focus is people close enough to the work that they can change product direction quickly: solo builders, founder teams, and small teams trying to turn messy product thinking into an actual product. Solo builders are the broader and easier-to-inspire adoption market; small teams capture the first-user founder/team context and the collaboration pressure that makes shared product intent matter. Larger teams, mature product organizations, and enterprise governance workflows are not the current wedge.

The first user is the builder of Outcome Engineering itself, operating in the small-team/founder context. This is intentional: the product should reach an MVP that solves a real product-judgment problem in its own development workflow before asking others to adopt it. Evidence will initially come from that first-user usage, then from trying to convince solo builders and other small teams to use the same practice.

## Strategic Pillars

### Teach the framework

Outcome Engineering teaches solo builders and small product-building teams a way to break product work into vision, strategy, ICPs, outcomes, opportunities, solutions, assumptions, PRDs, and delivery work. The framework should be learned through use, not through a large upfront explanation.

### Make the graph visually usable

The primary product surface should be a visual editor for the product graph. Builders should use it to break down complexity, inspect how work connects, stay aligned with the vision, and keep product context in the repo as their product and agent-assisted codebase evolve.

### Make the graph agent-legible

The graph should be structured so agents can inspect it, help build it, suggest updates, review current work against product intent, and answer practical questions like what to clarify, test, or build next. The CLI primarily exists as the agent and automation interface to this graph.

### Keep optional strategy tools separate

Outcome Engineering can include optional surfaces for deeper strategic thinking, such as a flywheel view, when they help the first user or early adopters clarify product logic. Those surfaces must remain optional and separate from the core graph so builders can use Outcome Engineering without needing a flywheel.
