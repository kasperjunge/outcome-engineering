#!/usr/bin/env python3
"""Create an example Outcome Engineering product graph directory."""

from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Node:
    slug: str
    kind: str
    title: str
    body: str
    children: dict[str, list["Node"]] = field(default_factory=dict)
    files: dict[str, str] = field(default_factory=dict)

    @property
    def marker_file(self) -> str:
        return f"{self.kind.upper()}.md"


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def render_node(node: Node) -> str:
    return f"""# {node.title}

```yaml
type: {node.kind}
id: {node.kind}.{node.slug}
status: example
```

{node.body}
"""


def write_node(base: Path, node: Node) -> None:
    node_dir = base / node.slug
    write_file(node_dir / node.marker_file, render_node(node))

    for relative_path, content in node.files.items():
        write_file(node_dir / relative_path, content)

    for relationship, children in node.children.items():
        for child in children:
            write_node(node_dir / relationship, child)


def example_graph() -> Node:
    return Node(
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
                Node(
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
                        "opportunities": [
                            Node(
                                slug="recurring-work-is-hard-to-describe",
                                kind="opportunity",
                                title="Recurring Work Is Hard To Describe",
                                body="""Users often know how to do a task themselves, but cannot easily describe the process, edge cases, inputs, and quality bar for an agent.""",
                                children={
                                    "solutions": [
                                        Node(
                                            slug="delegation-interview",
                                            kind="solution",
                                            title="Delegation Interview",
                                            body="""An agent-guided interview helps the user describe one concrete task, then expands outward to map related work.""",
                                            children={
                                                "assumptions": [
                                                    Node(
                                                        slug="interview-produces-better-task-descriptions",
                                                        kind="assumption",
                                                        title="Interview Produces Better Task Descriptions",
                                                        body="""If an agent interviews the user about a concrete recent task, the resulting task description will be more actionable than a blank-form prompt.""",
                                                        children={
                                                            "experiments": [
                                                                Node(
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
                                                    Node(
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
                Node(
                    slug="agents-lack-safe-access-to-tools",
                    kind="opportunity",
                    title="Agents Lack Safe Access To Tools",
                    body="""Even when a user knows what to delegate, the agent may lack safe, discoverable, permissioned access to the systems needed to do the work.""",
                    children={
                        "solutions": [
                            Node(
                                slug="agent-central",
                                kind="solution",
                                title="Agent Central",
                                body="""A capability platform where administrators configure and publish safe operations that agents can discover and execute through a small MCP surface.""",
                                children={
                                    "assumptions": [
                                        Node(
                                            slug="operation-discovery-reduces-tool-overload",
                                            kind="assumption",
                                            title="Operation Discovery Reduces Tool Overload",
                                            body="""Agents will perform better when they can search and describe operations instead of receiving a very large static tool list.""",
                                        ),
                                        Node(
                                            slug="admins-will-curate-agent-capabilities",
                                            kind="assumption",
                                            title="Admins Will Curate Agent Capabilities",
                                            body="""Organizations will assign someone to configure, publish, and govern the operations made available to agents.""",
                                        ),
                                    ],
                                    "experiments": [
                                        Node(
                                            slug="fake-connector-prototype",
                                            kind="experiment",
                                            title="Fake Connector Prototype",
                                            body="""Build an in-memory connector prototype and observe whether agents can discover, describe, and execute the right operation without needing one MCP tool per capability.""",
                                        )
                                    ],
                                    "prds": [
                                        Node(
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
            raise SystemExit(f"{root} already exists. Re-run with --force to replace it.")
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("examples/delegation-product-graph"),
        help="Directory to create. Defaults to examples/delegation-product-graph.",
    )
    parser.add_argument("--force", action="store_true", help="Replace the output directory if it already exists.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    create_example(args.output, args.force)
    print(f"Created example product graph at {args.output}")


if __name__ == "__main__":
    main()
