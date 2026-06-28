# Graph Structure Can Drift

```yaml
type: opportunity
id: opportunity.graph-structure-can-drift
status: active
```

As teams and agents edit files, the graph can accumulate invalid placements, duplicate ids, stale ICP references, or unsupported relationship folders.

## Evidence

- Manual markdown edits can break ids without moving files.
- New relationship types are tempting to add before the model supports them.

## Known / Unknown

- Known: validation catches structural mistakes.
- Unknown: whether the UI should prevent every invalid edit or allow draft-invalid states.
