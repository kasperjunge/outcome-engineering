# Skills Improve Agent Output

```yaml
type: assumption-test
id: assumption-test.skills-improve-agent-output
status: planned
```

## Assumption

Installing the Outcome Engineering skill causes agents to use the CLI and preserve graph structure more reliably.

## Risk Type

Value.

## Test

Run paired graph-edit tasks with and without the installed skill and compare validation failures.

## Success / Failure Signal

Success: skilled agents validate on the first attempt more often and read deterministic context before edits. Failure: no measurable difference.

## Decision It Informs

Whether install UX should remain a first-class workflow.
