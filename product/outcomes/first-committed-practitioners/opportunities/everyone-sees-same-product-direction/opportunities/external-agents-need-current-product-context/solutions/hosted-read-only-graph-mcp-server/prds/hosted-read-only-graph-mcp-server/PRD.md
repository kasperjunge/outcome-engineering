---
type: prd
id: prd.hosted-read-only-graph-mcp-server
status: draft
---

# Hosted read-only graph MCP server

## Problem

External chat agents can help users reason about product strategy, PRDs, tradeoffs, and implementation plans, but they often do not have a repo checkout and cannot run the local `oe` CLI. Without a hosted context interface, the user must manually paste graph content into the conversation.

Manual context sharing is incomplete and stale-prone. An agent may answer without seeing the current strategy, the relevant ICP, the parent outcome, the opportunity behind a solution, or the PRD currently being implemented. That weakens Outcome Engineering's goal of keeping agent-assisted work connected to product intent.

## Goal

An authorized external chat agent can connect to an HTTP MCP server and retrieve current, read-only product graph context from the hosted graph without repo access.

The first version should make the graph useful as agent context, not as a general remote filesystem. It should provide deterministic graph views, concise node content, trace paths, and provenance so an agent can ground its answers in the current product graph.

## User Stories

- As a product builder, I want to connect an external chat agent to my hosted product graph so I do not have to paste product context manually.
- As an external agent, I want to retrieve the current strategy, ICPs, outcomes, opportunities, solutions, assumption tests, and PRDs so I can answer with product context.
- As a product builder, I want the MCP server to be read-only so external agents cannot mutate the graph.
- As an external agent, I want to trace a node back to its parent outcome and strategy context so I understand why the work matters.
- As a product builder, I want MCP responses to include source/version metadata so I can tell what graph state the agent used.

## Acceptance Criteria

1. The hosted graph exposes an authenticated HTTP MCP server.
2. Unauthorized clients cannot access product graph content.
3. Authorized MCP clients can list available graph nodes by kind.
4. Authorized MCP clients can retrieve a node's readable content by node id or slug.
5. Authorized MCP clients can retrieve a trace for a node, including ancestors up to the outcome and relevant higher-level product context.
6. Authorized MCP clients can retrieve deterministic agent context for a node, equivalent in intent to local `oe context`.
7. Authorized MCP clients can retrieve current strategy context.
8. Authorized MCP clients can retrieve active or draft PRDs.
9. MCP responses include node ids, node kinds, trace paths, and hosted graph source/version metadata.
10. The MCP server does not expose create, update, delete, or graph-reorganization operations.
11. The MCP server reflects the same current hosted graph source as the read-only web view.
12. Error responses distinguish missing nodes, ambiguous slugs, unauthorized access, and unavailable graph snapshots.

## Scope

### In scope

- Authenticated HTTP MCP access to the current hosted product graph.
- Read-only tools or resources for listing, showing, tracing, and contextualizing graph nodes.
- Agent-oriented response shapes that are structured, concise, and provenance-aware.
- Support for external chat agents without local repo checkout or local `oe` CLI access.

### Out of scope

- Editing graph nodes through MCP.
- Creating PRDs, opportunities, solutions, or assumption tests through MCP.
- Branch selection, historical graph versions, or multi-graph management.
- General access to arbitrary repository files.
- Agent-side prompting, memory, or reasoning features outside the MCP server.

## Open Questions

- Should the first MCP surface be tool-based, resource-based, or both?
- What is the minimum useful auth model for a first hosted version: personal token, OAuth client, or per-graph MCP token?
- Should MCP expose raw markdown, normalized structured content, or both?
- How much search is needed in the first version, versus requiring agents to list and inspect nodes directly?
- Should PRD retrieval have a dedicated shortcut, or should PRDs be handled only through generic graph node tools?
