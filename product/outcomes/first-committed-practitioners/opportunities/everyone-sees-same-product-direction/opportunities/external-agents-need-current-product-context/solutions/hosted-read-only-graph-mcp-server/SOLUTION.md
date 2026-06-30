---
type: solution
id: solution.hosted-read-only-graph-mcp-server
status: draft
---

# Hosted read-only graph MCP server

Provide an authenticated HTTP MCP server that exposes the current hosted OE product graph as read-only product context for external agents.

An external chat agent without a repo checkout can connect to the MCP server, inspect the current graph, retrieve strategy and ICP context, trace a PRD back to its parent outcome and opportunity, and answer product questions with explicit graph provenance. The server should mirror the most useful local `oe` context workflows while hiding filesystem details that are not meaningful outside the repo.

The MCP server is not an editing interface. It does not create, update, delete, or reorganize graph nodes. Its purpose is to make current product intent portable to agent surfaces that cannot run local commands.

## Product Risks

- Value: External agents may not use graph context well enough to improve product conversations or implementation planning.
- Usability: If the MCP surface exposes too many low-level graph details, agents may retrieve noisy context or miss the right node.
- Feasibility: The hosted server must serve current, validated graph data reliably and identify the graph version it reflects.
- Viability: Authentication and token management must protect private product intent without making the early hosted workflow heavy.

## Assumptions

- External chat agents need product context even when they do not have repo access.
- A read-only MCP interface is enough for the first remote-agent use case.
- The local `oe context`, `oe trace`, `oe show`, and `oe list` workflows are good starting points for MCP tools.
- Agents make better product recommendations when responses include node IDs, trace paths, and source/version metadata.
- Editing should remain repo-native until there is clear evidence that remote agents need write access.
