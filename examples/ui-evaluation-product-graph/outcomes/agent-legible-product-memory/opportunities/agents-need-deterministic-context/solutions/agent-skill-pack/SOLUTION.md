# Agent Skill Pack

```yaml
type: solution
id: solution.agent-skill-pack
status: active
```

Installable agent skills teach Codex and Claude how to inspect, create, validate, and trace product graph changes.

## Product Risks

- Value: users may not install skills until they already trust the tool.
- Usability: skill instructions can become stale relative to CLI behavior.
- Feasibility: packaging must support multiple agent directory conventions.
- Viability: skills are a distribution channel for agent-native workflows.

## Assumptions

- Agent instructions materially improve graph-edit quality.
- Users want repo-local skills as well as personal global skills.
