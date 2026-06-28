# Users Fix Path-Based Issues

```yaml
type: assumption-test
id: assumption-test.users-fix-path-based-issues
status: not-started
```

## Assumption

Users can resolve validation errors when given exact paths and clear messages.

## Risk Type

Usability.

## Test

Seed three invalid graphs and observe whether users can repair them from UI messages.

## Success / Failure Signal

Success: users repair two of three seeded issues without maintainer help. Failure: messages require framework knowledge.

## Decision It Informs

Whether validation messages need richer remediation actions.
