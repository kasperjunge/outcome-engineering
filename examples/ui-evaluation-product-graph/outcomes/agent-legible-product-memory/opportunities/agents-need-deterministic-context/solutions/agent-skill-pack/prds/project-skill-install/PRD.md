# Project Skill Install

```yaml
type: prd
id: prd.project-skill-install
status: active
```

## Problem

Teams need agent instructions inside a repo so contributors use the same graph workflow.

## User Stories

- As a maintainer, I can install project-local skills for Claude or Codex style directories.
- As a contributor, my agent can discover the repo's Outcome Engineering workflow.
- As a tool maintainer, I can update bundled skills through the package.

## Acceptance Criteria

- `oe install --skills` installs bundled skills into project-local agent directories.
- `oe install --skills=agents` supports `.agents/skills`.
- Existing skill directories are protected unless `--force` is passed.
- Tests cover target path selection.
