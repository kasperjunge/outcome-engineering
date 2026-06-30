---
type: assumption-test
id: assumption-test.external-agent-context-improves-product-alignment
status: draft
---

# External agent context improves product alignment

## Assumption

External chat agents give more useful product and implementation guidance when they can retrieve current OE graph context through a hosted read-only MCP server instead of relying on manually pasted context.

## Risk Type

Value

## Test

Use the same product question or implementation-planning prompt with two agent sessions:

1. A baseline session where the user manually describes the product context.
2. An MCP-enabled session where the agent can inspect the hosted graph through read-only tools.

Compare whether the MCP-enabled agent identifies the relevant strategy, ICP, outcome, opportunity, solution, and PRD context with less manual prompting. Include at least one prompt about a current PRD and one prompt about whether a proposed feature fits the current strategy.

## Success / Failure Signal

Success: the MCP-enabled agent grounds its answer in the correct graph nodes, asks fewer context-recovery questions, avoids contradicting the current strategy, and produces advice the builder judges more aligned with product intent.

Failure: the MCP-enabled agent ignores the graph, retrieves irrelevant context, overstates what the graph says, or produces advice no better than the manually prompted baseline.

## Decision It Informs

Whether a hosted read-only MCP server is a valuable near-term part of the hosted graph work, and which MCP tools should be included in the first implementation.
