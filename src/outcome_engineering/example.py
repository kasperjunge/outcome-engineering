from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ExampleNode:
    slug: str
    kind: str
    title: str
    body: str
    children: dict[str, list["ExampleNode"]] = field(default_factory=dict)
    files: dict[str, str] = field(default_factory=dict)

    @property
    def marker_file(self) -> str:
        return f"{self.kind.upper()}.md"


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def render_node(node: ExampleNode) -> str:
    return f"""# {node.title}

```yaml
type: {node.kind}
id: {node.kind}.{node.slug}
status: example
```

{node.body}
"""


def write_node(base: Path, node: ExampleNode) -> None:
    node_dir = base / node.slug
    write_file(node_dir / node.marker_file, render_node(node))

    for relative_path, content in node.files.items():
        write_file(node_dir / relative_path, content)

    for relationship, children in node.children.items():
        for child in children:
            write_node(node_dir / relationship, child)


def example_graph() -> ExampleNode:
    return ExampleNode(
        slug="delegation-confidence",
        kind="outcome",
        title="Delegation Confidence",
        body="""Knowledge workers trust delegated agent work enough to use it for real recurring tasks.

## Measures

- A user delegates at least one recurring task to an agent.
- The delegated task completes with reviewable output.
- The user would choose to delegate the same task again.

## Known / Unknown

- Known: users want help turning messy work into agent-usable instructions.
- Unknown: whether safe tool access or better task framing is the larger blocker.""",
        files={
            "notes.md": """# Notes

This outcome is intentionally broad enough to contain multiple opportunity branches.
""",
        },
        children={
            "opportunities": [
                ExampleNode(
                    slug="users-do-not-know-what-to-delegate",
                    kind="opportunity",
                    title="Users Do Not Know What To Delegate",
                    body="""Users can sense that agents could help, but they struggle to identify which parts of their work are good delegation candidates.

## Evidence

- Workshop participants often start with vague work categories instead of concrete recurring tasks.
- Delegation candidates become clearer after an interview about recent work.""",
                    files={
                        "evidence/interview-patterns.md": """# Interview Patterns

Example evidence placeholder. In a real product graph this would link to interview notes, clips, transcripts, or synthesis.
""",
                    },
                    children={
                        "assumptions": [
                            ExampleNode(
                                slug="delegation-pain-is-frequent",
                                kind="assumption",
                                title="Delegation Pain Is Frequent",
                                body="""Users run into this uncertainty often enough that solving it would materially increase delegation confidence.""",
                                children={
                                    "experiments": [
                                        ExampleNode(
                                            slug="frequency-interviews",
                                            kind="experiment",
                                            title="Frequency Interviews",
                                            body="""Interview users about recent work and count how often they wanted to delegate something but could not identify a concrete agent-ready task.""",
                                        )
                                    ]
                                },
                            )
                        ],
                        "opportunities": [
                            ExampleNode(
                                slug="recurring-work-is-hard-to-describe",
                                kind="opportunity",
                                title="Recurring Work Is Hard To Describe",
                                body="""Users often know how to do a task themselves, but cannot easily describe the process, edge cases, inputs, and quality bar for an agent.""",
                                children={
                                    "solutions": [
                                        ExampleNode(
                                            slug="delegation-interview",
                                            kind="solution",
                                            title="Delegation Interview",
                                            body="""An agent-guided interview helps the user describe one concrete task, then expands outward to map related work.""",
                                            children={
                                                "assumptions": [
                                                    ExampleNode(
                                                        slug="interview-produces-better-task-descriptions",
                                                        kind="assumption",
                                                        title="Interview Produces Better Task Descriptions",
                                                        body="""If an agent interviews the user about a concrete recent task, the resulting task description will be more actionable than a blank-form prompt.""",
                                                        children={
                                                            "experiments": [
                                                                ExampleNode(
                                                                    slug="compare-blank-form-vs-interview",
                                                                    kind="experiment",
                                                                    title="Compare Blank Form Vs Interview",
                                                                    body="""Ask users to describe the same delegation candidate through a blank form and through an interview. Compare completeness, confidence, and agent execution quality.""",
                                                                )
                                                            ]
                                                        },
                                                    )
                                                ],
                                                "prds": [
                                                    ExampleNode(
                                                        slug="delegation-interview-mvp",
                                                        kind="prd",
                                                        title="Delegation Interview MVP",
                                                        body="""Build the smallest flow that interviews a user about one recurring task and turns the answers into a reusable agent instruction artifact.

## Acceptance Criteria

- The interview anchors on one concrete recent task.
- The output includes inputs, steps, edge cases, quality bar, and stop-and-ask conditions.
- The output can be used by an agent in a fresh context.""",
                                                    )
                                                ],
                                            },
                                        )
                                    ]
                                },
                            )
                        ]
                    },
                ),
                ExampleNode(
                    slug="agents-lack-safe-access-to-tools",
                    kind="opportunity",
                    title="Agents Lack Safe Access To Tools",
                    body="""Even when a user knows what to delegate, the agent may lack safe, discoverable, permissioned access to the systems needed to do the work.""",
                    children={
                        "solutions": [
                            ExampleNode(
                                slug="agent-central",
                                kind="solution",
                                title="Agent Central",
                                body="""A capability platform where administrators configure and publish safe operations that agents can discover and execute through a small MCP surface.""",
                                children={
                                    "assumptions": [
                                        ExampleNode(
                                            slug="operation-discovery-reduces-tool-overload",
                                            kind="assumption",
                                            title="Operation Discovery Reduces Tool Overload",
                                            body="""Agents will perform better when they can search and describe operations instead of receiving a very large static tool list.""",
                                            children={
                                                "experiments": [
                                                    ExampleNode(
                                                        slug="fake-connector-prototype",
                                                        kind="experiment",
                                                        title="Fake Connector Prototype",
                                                        body="""Build an in-memory connector prototype and observe whether agents can discover, describe, and execute the right operation without needing one MCP tool per capability.""",
                                                    )
                                                ]
                                            },
                                        ),
                                        ExampleNode(
                                            slug="admins-will-curate-agent-capabilities",
                                            kind="assumption",
                                            title="Admins Will Curate Agent Capabilities",
                                            body="""Organizations will assign someone to configure, publish, and govern the operations made available to agents.""",
                                        ),
                                    ],
                                    "prds": [
                                        ExampleNode(
                                            slug="agent-central-mvp",
                                            kind="prd",
                                            title="Agent Central MVP",
                                            body="""Validate the smallest useful loop for low-context agent operation discovery and execution.

## Acceptance Criteria

- Agents can search operations.
- Agents can describe a selected operation.
- Agents can execute a valid GraphQL operation.
- Runtime permission checks allow or deny execution.""",
                                        )
                                    ],
                                },
                            )
                        ]
                    },
                ),
            ]
        },
    )


def create_example(root: Path, force: bool) -> None:
    if root.exists():
        if not force:
            raise FileExistsError(f"{root} already exists. Re-run with --force to replace it.")
        shutil.rmtree(root)

    write_file(
        root / "VISION.md",
        """# Vision

Enable knowledge workers to securely and effectively delegate work to AI agents.
""",
    )
    write_file(
        root / "STRATEGY.md",
        """# Strategy

Focus on recurring knowledge work where better task framing and safer tool access can make delegation feel trustworthy.
""",
    )
    write_node(root / "outcomes", example_graph())
