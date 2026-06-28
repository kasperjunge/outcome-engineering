# Context Reduces Wrong Edits

```yaml
type: assumption-test
id: assumption-test.context-reduces-wrong-edits
status: completed
```

## Assumption

Providing deterministic node context reduces misplaced or off-strategy graph edits by agents.

## Risk Type

Value and feasibility.

## Test

Ask agents to draft PRDs with and without `oe context`, then review trace correctness.

## Success / Failure Signal

Success: context-assisted drafts have fewer missing parent references and fewer unsupported assumptions. Failure: context does not change review quality.

## Decision It Informs

Whether agent skills should require `oe context` before PRD and implementation work.
