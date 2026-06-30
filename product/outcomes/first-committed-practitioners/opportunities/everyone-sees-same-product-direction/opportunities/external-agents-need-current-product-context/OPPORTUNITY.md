---
type: opportunity
id: opportunity.external-agents-need-current-product-context
status: draft
---

# External agents need current product context without repo access

Small product-building teams increasingly use external chat agents to think through product decisions, PRDs, implementation plans, and tradeoffs. Those agents often do not have a local checkout of the repo and cannot run the `oe` CLI, so they depend on whatever product context the user manually pastes into the conversation.

That makes product intent fragile. The agent may miss the current strategy, misunderstand the active outcome, ignore a relevant ICP, or advise on a PRD without seeing how it connects to the rest of the graph. The user then has to act as the context bridge instead of letting the product graph serve as durable shared memory.

This is part of the larger shared-direction problem: humans need a browser-accessible graph, and agents need a structured read-only context interface. Both should reflect the same current product graph without requiring local setup.

## Evidence

- Hypothesis: "I want to ask an external chat agent about this product without pasting the whole graph into the conversation."
- Hypothesis: "I want an agent to understand the current strategy, outcomes, and PRDs even when it is not running in my repo."
- Hypothesis: Hosted read-only graph access can make product context portable across agent surfaces without giving those agents edit access.

## Known / Unknown

- Known: The current strategy says the graph should be agent-legible.
- Known: The `oe context` command already defines a useful local pattern for deterministic agent context.
- Known: The hosted read-only graph solution creates the right source for a remote read-only graph surface.
- Unknown: Which MCP tools or resources external agents need most often.
- Unknown: Whether external agents use structured graph context well enough to improve product discussions.
- Unknown: What authentication and scoping model is lightweight enough for early users while still protecting private product intent.
