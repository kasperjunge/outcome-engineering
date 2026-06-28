from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from outcome_engineering.model import KIND_TO_MARKER_FILE


@dataclass(frozen=True)
class ExampleNode:
    slug: str
    kind: str
    title: str
    body: str
    status: str = "example"
    children: dict[str, list["ExampleNode"]] = field(default_factory=dict)
    files: dict[str, str] = field(default_factory=dict)
    icps: list[str] = field(default_factory=list)

    @property
    def marker_file(self) -> str:
        return KIND_TO_MARKER_FILE[self.kind]


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def render_node(node: ExampleNode) -> str:
    icp_block = ""
    if node.icps:
        icp_block = "icps:\n" + "".join(f"  - {ref}\n" for ref in node.icps)
    return f"""# {node.title}

```yaml
type: {node.kind}
id: {node.kind}.{node.slug}
{icp_block}status: {node.status}
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
        icps=["icp.solo-knowledge-worker"],
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
                                                "assumption-tests": [
                                                    ExampleNode(
                                                        slug="interview-produces-better-task-descriptions",
                                                        kind="assumption-test",
                                                        title="Interview Produces Better Task Descriptions",
                                                        body="""Assumption: if an agent interviews the user about a concrete recent task, the resulting task description will be more actionable than a blank-form prompt.

Test: ask users to describe the same delegation candidate through a blank form and through an interview. Compare completeness, confidence, and agent execution quality.""",
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
                                    "assumption-tests": [
                                        ExampleNode(
                                            slug="operation-discovery-reduces-tool-overload",
                                            kind="assumption-test",
                                            title="Operation Discovery Reduces Tool Overload",
                                            body="""Assumption: agents will perform better when they can search and describe operations instead of receiving a very large static tool list.

Test: build an in-memory connector prototype and observe whether agents can discover, describe, and execute the right operation without needing one MCP tool per capability.""",
                                        ),
                                        ExampleNode(
                                            slug="admins-will-curate-agent-capabilities",
                                            kind="assumption-test",
                                            title="Admins Will Curate Agent Capabilities",
                                            body="""Assumption: organizations will assign someone to configure, publish, and govern the operations made available to agents.

Test: not yet designed. Identify whether early-access organizations name an owner for agent capability curation.""",
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


def example_icps() -> list[ExampleNode]:
    return [
        ExampleNode(
            slug="solo-knowledge-worker",
            kind="icp",
            title="Solo Knowledge Worker",
            body="""## Who They Are

An independent operator or small-team lead who already works alongside AI agents and owns their own recurring workflows end to end.

## Jobs / Pains

- Wants to offload recurring, well-understood work without becoming a prompt engineer.
- Distrusts agent output they cannot quickly review.

## Why They Choose Us

- We help them turn messy real work into agent-usable instructions and keep the result reviewable.

## Where They Are Not A Fit

- Large orgs that need central governance and audited tool access before any delegation happens.""",
        ),
    ]


def comprehensive_graphs() -> list[ExampleNode]:
    return [
        ExampleNode(
            slug="team-alignment",
            kind="outcome",
            title="Team Alignment",
            status="active",
            icps=["icp.founder-product-lead", "icp.agency-delivery-lead"],
            body="""Product teams can explain why current work matters and where it sits in the larger product graph.

## Measures

- 80% of active nodes have a clear parent trace to an outcome.
- Weekly planning reviews reference the graph instead of a separate roadmap doc.
- At least three team members edit or comment on the graph in a month.

## Known / Unknown

- Known: visual structure makes drift easier to notice in product discussions.
- Unknown: whether teams want this as a standalone graph or embedded in existing planning rituals.""",
            files={
                "evidence/planning-review-notes.md": """# Planning Review Notes

- Teams liked seeing ICP, outcome, and solution context together.
- Reviewers asked for fast ways to collapse noisy branches.
- Several comments focused on stale assumptions hiding inside old PRDs.
""",
            },
            children={
                "opportunities": [
                    ExampleNode(
                        slug="strategy-is-separated-from-delivery",
                        kind="opportunity",
                        title="Strategy Is Separated From Delivery",
                        status="validated",
                        icps=["icp.founder-product-lead"],
                        body="""Teams keep strategy, discovery, PRDs, and implementation notes in different places, so the reason behind a task decays before delivery starts.

## Evidence

- Product leads described repeating the same context in Linear, Notion, Slack, and pull requests.
- Engineers asked which customer pain a task was meant to resolve after implementation had already begun.

## Known / Unknown

- Known: traceability matters most around prioritization and scope cuts.
- Unknown: whether lightweight markdown links are enough, or whether the graph must own delivery handoff.""",
                        children={
                            "opportunities": [
                                ExampleNode(
                                    slug="handoff-context-gets-lost",
                                    kind="opportunity",
                                    title="Handoff Context Gets Lost",
                                    status="active",
                                    body="""By the time a solution reaches implementation, teams often retain requirements but lose the assumptions and tradeoffs that shaped them.""",
                                    children={
                                        "solutions": [
                                            ExampleNode(
                                                slug="traceable-prd-panel",
                                                kind="solution",
                                                title="Traceable PRD Panel",
                                                status="ready",
                                                body="""A side panel shows a PRD beside its outcome, opportunity, solution, and assumption tests so reviewers can inspect intent without leaving the graph.

## Product Risks

- Value: teams may only need trace context during reviews, not all the time.
- Usability: dense context can overwhelm small screens.
- Feasibility: markdown editing and preview must stay responsive with large files.
- Viability: the feature is only valuable if teams keep PRDs in the graph.

## Assumptions

- Reviewers will use trace context before approving scope changes.
- Compact summaries are enough for daily use, with full markdown available on demand.""",
                                                children={
                                                    "assumption-tests": [
                                                        ExampleNode(
                                                            slug="reviewers-use-trace-context",
                                                            kind="assumption-test",
                                                            title="Reviewers Use Trace Context",
                                                            status="planned",
                                                            body="""## Assumption

Reviewers will open trace context during PRD and implementation review.

## Risk Type

Value and usability.

## Test

Instrument panel opens and run five moderated review sessions with intentionally ambiguous PRDs.

## Success / Failure Signal

Success: four of five reviewers use trace context before deciding. Failure: reviewers ignore it or ask for a separate summary.

## Decision It Informs

Whether trace context should be a primary panel or a secondary command.""",
                                                        ),
                                                        ExampleNode(
                                                            slug="summaries-are-enough",
                                                            kind="assumption-test",
                                                            title="Summaries Are Enough",
                                                            status="blocked",
                                                            body="""## Assumption

Short generated summaries provide enough context for most review decisions.

## Risk Type

Usability and trust.

## Test

Compare review outcomes with full markdown context, generated summaries, and no context.

## Success / Failure Signal

Success: summary users make comparable decisions and report lower cognitive load. Failure: users mistrust summaries or miss key constraints.

## Decision It Informs

Whether summary generation belongs in the MVP.""",
                                                        ),
                                                    ],
                                                    "prds": [
                                                        ExampleNode(
                                                            slug="traceable-prd-panel-mvp",
                                                            kind="prd",
                                                            title="Traceable PRD Panel MVP",
                                                            status="ready",
                                                            body="""## Problem

Reviewers cannot quickly inspect why a PRD exists or which assumptions it depends on.

## User Stories

- As a product lead, I can select a PRD and see its full trace.
- As an engineer, I can inspect assumptions before proposing a scope cut.
- As a reviewer, I can jump from the PRD to the exact opportunity it addresses.

## Acceptance Criteria

- The panel lists all ancestors from outcome to solution.
- The panel shows sibling assumption tests and their statuses.
- The PRD body remains editable without losing scroll position.
- The UI handles long markdown without overlapping graph controls.""",
                                                        )
                                                    ],
                                                },
                                            )
                                        ]
                                    },
                                ),
                                ExampleNode(
                                    slug="old-decisions-are-hard-to-challenge",
                                    kind="opportunity",
                                    title="Old Decisions Are Hard To Challenge",
                                    status="backlog",
                                    body="""Archived decisions sit in old docs and are difficult to revisit when new evidence appears.""",
                                ),
                            ],
                            "solutions": [
                                ExampleNode(
                                    slug="focus-mode",
                                    kind="solution",
                                    title="Focus Mode",
                                    status="active",
                                    body="""A graph view that narrows to one outcome and its trace subtree while keeping ICP and strategy context visible.

## Product Risks

- Value: a narrowed graph may hide useful adjacent context.
- Usability: users need obvious controls for moving back to the overview.
- Feasibility: layout should stay stable when branches expand and collapse.
- Viability: focus mode must make the editor feel clearer than a file tree.

## Assumptions

- Teams mostly discuss one outcome at a time.
- A focused graph reduces cognitive load during product review.""",
                                    children={
                                        "assumption-tests": [
                                            ExampleNode(
                                                slug="teams-discuss-one-outcome",
                                                kind="assumption-test",
                                                title="Teams Discuss One Outcome",
                                                status="running",
                                                body="""## Assumption

Most product review conversations center on one outcome and its immediate branches.

## Risk Type

Value.

## Test

Observe three live reviews and tag every navigation jump by graph distance.

## Success / Failure Signal

Success: 70% of discussion stays within one outcome subtree. Failure: teams constantly need cross-outcome comparison.

## Decision It Informs

Whether the default UI should open in overview or focused outcome mode.""",
                                            )
                                        ],
                                        "prds": [
                                            ExampleNode(
                                                slug="outcome-focus-mode",
                                                kind="prd",
                                                title="Outcome Focus Mode",
                                                status="active",
                                                body="""## Problem

Large product graphs become too noisy for planning discussions.

## User Stories

- As a facilitator, I can enter an outcome-focused view from the overview.
- As a participant, I can expand and collapse branches without losing orientation.
- As a product lead, I can still see which ICPs the focused outcome serves.

## Acceptance Criteria

- Clicking an outcome redraws the view around that outcome.
- The focused view includes opportunities, solutions, assumption tests, and PRDs.
- The overview is reachable in one action.
- Node selection persists when switching between overview and focus.""",
                                            )
                                        ],
                                    },
                                )
                            ],
                        },
                    ),
                    ExampleNode(
                        slug="icp-fit-is-implicit",
                        kind="opportunity",
                        title="ICP Fit Is Implicit",
                        status="discovery",
                        icps=["icp.agency-delivery-lead", "icp.enterprise-product-ops"],
                        body="""Teams make prioritization decisions without making the target customer profile explicit.

## Evidence

- Reviewers asked whether the same feature served agencies, startups, and enterprise product ops equally.
- ICP notes were present in strategy docs but not visible near outcome decisions.

## Known / Unknown

- Known: ICP references make the graph easier to challenge.
- Unknown: whether users understand many-to-many ICP links without onboarding.""",
                        children={
                            "solutions": [
                                ExampleNode(
                                    slug="icp-reference-edges",
                                    kind="solution",
                                    title="ICP Reference Edges",
                                    status="shipped",
                                    body="""Render ICP references as non-structural edges so the UI distinguishes who a node serves from the trace hierarchy.

## Product Risks

- Value: users may not care about ICPs in early graphs.
- Usability: extra edges can create visual clutter.
- Feasibility: the graph serializer must keep structural and ICP edges separate.
- Viability: ICP links support positioning and sales conversations later.

## Assumptions

- Users can understand two edge types when they are visually distinct.
- ICP links are useful at outcome and opportunity levels, but noisy below that.""",
                                    children={
                                        "assumption-tests": [
                                            ExampleNode(
                                                slug="users-understand-edge-types",
                                                kind="assumption-test",
                                                title="Users Understand Edge Types",
                                                status="completed",
                                                body="""## Assumption

Users can distinguish structural trace edges from ICP reference edges.

## Risk Type

Usability.

## Test

Show five users a mixed graph and ask them to explain what each edge means.

## Success / Failure Signal

Success: four of five users describe both edge types correctly. Failure: users read ICP edges as parent-child hierarchy.

## Decision It Informs

Whether edge legends and styling need to ship in the first visual editor.""",
                                            )
                                        ],
                                        "prds": [
                                            ExampleNode(
                                                slug="icp-edge-rendering",
                                                kind="prd",
                                                title="ICP Edge Rendering",
                                                status="shipped",
                                                body="""## Problem

The UI needs to show which ICPs an outcome or opportunity serves without breaking the trace tree.

## User Stories

- As a user, I can see ICP relationships as distinct from structural hierarchy.
- As a reviewer, I can identify which outcomes serve a selected ICP.
- As an editor, I can inspect ICP references in the selected node body.

## Acceptance Criteria

- ICP nodes render in the overview.
- ICP edges use a separate edge type in the graph payload.
- ICP nodes list served-by references.
- Validation rejects unknown ICP references.""",
                                            )
                                        ],
                                    },
                                ),
                            ]
                        },
                    ),
                ]
            },
        ),
        ExampleNode(
            slug="agent-legible-product-memory",
            kind="outcome",
            title="Agent-Legible Product Memory",
            status="active",
            icps=["icp.agent-native-builder", "icp.enterprise-product-ops"],
            body="""Agents can inspect the graph, retrieve relevant context, and help teams maintain product intent without inventing missing structure.

## Measures

- Agents can answer trace questions using `oe context`.
- New nodes created by agents validate without manual directory repair.
- Agent-written PRDs reference assumptions and parent opportunities.

## Known / Unknown

- Known: deterministic filesystem structure is easier for agents than opaque SaaS state.
- Unknown: how much judgment agents should apply before asking the human.""",
            files={
                "research/agent-session-notes.md": """# Agent Session Notes

Agents performed well when asked to trace a specific node id.
They struggled when a graph contained stale or ambiguous slugs.
""",
            },
            children={
                "opportunities": [
                    ExampleNode(
                        slug="agents-need-deterministic-context",
                        kind="opportunity",
                        title="Agents Need Deterministic Context",
                        status="validated",
                        body="""Agents need a stable way to retrieve ancestors, children, ICPs, and supporting files around a node.

## Evidence

- Ad hoc file search produced inconsistent context windows.
- `oe context` reduced irrelevant file reads during PRD drafting.

## Known / Unknown

- Known: trace context is needed before editing or implementation work.
- Unknown: whether evidence files should be inlined, summarized, or only linked.""",
                        children={
                            "solutions": [
                                ExampleNode(
                                    slug="context-command",
                                    kind="solution",
                                    title="Context Command",
                                    status="shipped",
                                    body="""A CLI command prints deterministic context for a selected node, including trace, ICPs, children, supporting files, and marker content.

## Product Risks

- Value: context output may be too verbose for small tasks.
- Usability: selectors must be forgiving but not ambiguous.
- Feasibility: output must remain deterministic as graph rules evolve.
- Viability: agent workflows depend on stable command contracts.

## Assumptions

- Agents benefit from structured context before editing graph nodes.
- Humans can still read the output when debugging agent behavior.""",
                                    children={
                                        "assumption-tests": [
                                            ExampleNode(
                                                slug="context-reduces-wrong-edits",
                                                kind="assumption-test",
                                                title="Context Reduces Wrong Edits",
                                                status="completed",
                                                body="""## Assumption

Providing deterministic node context reduces misplaced or off-strategy graph edits by agents.

## Risk Type

Value and feasibility.

## Test

Ask agents to draft PRDs with and without `oe context`, then review trace correctness.

## Success / Failure Signal

Success: context-assisted drafts have fewer missing parent references and fewer unsupported assumptions. Failure: context does not change review quality.

## Decision It Informs

Whether agent skills should require `oe context` before PRD and implementation work.""",
                                            )
                                        ],
                                        "prds": [
                                            ExampleNode(
                                                slug="context-command-contract",
                                                kind="prd",
                                                title="Context Command Contract",
                                                status="shipped",
                                                body="""## Problem

Agents need deterministic context around a graph node before they can safely write product artifacts.

## User Stories

- As an agent, I can request context by id, slug, directory, or marker path.
- As a human reviewer, I can see the exact context an agent used.
- As a tool author, I can rely on a stable output shape.

## Acceptance Criteria

- The command validates the graph before printing context.
- The output includes trace, ICPs, children, supporting files, ancestor content, ICP content, and node content.
- Ambiguous selectors fail instead of guessing.
- Output order is deterministic.""",
                                            )
                                        ],
                                    },
                                ),
                                ExampleNode(
                                    slug="agent-skill-pack",
                                    kind="solution",
                                    title="Agent Skill Pack",
                                    status="active",
                                    body="""Installable agent skills teach Codex and Claude how to inspect, create, validate, and trace product graph changes.

## Product Risks

- Value: users may not install skills until they already trust the tool.
- Usability: skill instructions can become stale relative to CLI behavior.
- Feasibility: packaging must support multiple agent directory conventions.
- Viability: skills are a distribution channel for agent-native workflows.

## Assumptions

- Agent instructions materially improve graph-edit quality.
- Users want repo-local skills as well as personal global skills.""",
                                    children={
                                        "assumption-tests": [
                                            ExampleNode(
                                                slug="skills-improve-agent-output",
                                                kind="assumption-test",
                                                title="Skills Improve Agent Output",
                                                status="planned",
                                                body="""## Assumption

Installing the Outcome Engineering skill causes agents to use the CLI and preserve graph structure more reliably.

## Risk Type

Value.

## Test

Run paired graph-edit tasks with and without the installed skill and compare validation failures.

## Success / Failure Signal

Success: skilled agents validate on the first attempt more often and read deterministic context before edits. Failure: no measurable difference.

## Decision It Informs

Whether install UX should remain a first-class workflow.""",
                                            )
                                        ],
                                        "prds": [
                                            ExampleNode(
                                                slug="project-skill-install",
                                                kind="prd",
                                                title="Project Skill Install",
                                                status="active",
                                                body="""## Problem

Teams need agent instructions inside a repo so contributors use the same graph workflow.

## User Stories

- As a maintainer, I can install project-local skills for Claude or Codex style directories.
- As a contributor, my agent can discover the repo's Outcome Engineering workflow.
- As a tool maintainer, I can update bundled skills through the package.

## Acceptance Criteria

- `oe install --skills` installs bundled skills into project-local agent directories.
- `oe install --skills=agents` supports `.agents/skills`.
- Existing skill directories are protected unless `--force` is passed.
- Tests cover target path selection.""",
                                            )
                                        ],
                                    },
                                ),
                            ]
                        },
                    ),
                    ExampleNode(
                        slug="graph-structure-can-drift",
                        kind="opportunity",
                        title="Graph Structure Can Drift",
                        status="active",
                        body="""As teams and agents edit files, the graph can accumulate invalid placements, duplicate ids, stale ICP references, or unsupported relationship folders.

## Evidence

- Manual markdown edits can break ids without moving files.
- New relationship types are tempting to add before the model supports them.

## Known / Unknown

- Known: validation catches structural mistakes.
- Unknown: whether the UI should prevent every invalid edit or allow draft-invalid states.""",
                        children={
                            "solutions": [
                                ExampleNode(
                                    slug="live-validation-panel",
                                    kind="solution",
                                    title="Live Validation Panel",
                                    status="planned",
                                    body="""Show validation issues directly in the UI after edits and structural mutations.

## Product Risks

- Value: validation issues may be rare in normal use.
- Usability: users need clear paths from issue to file and node.
- Feasibility: validation must run fast after each edit.
- Viability: better validation reduces support load for graph corruption.

## Assumptions

- Users will fix validation issues when shown exact paths.
- Allowing invalid marker edits is safer than rejecting and losing work.""",
                                    children={
                                        "assumption-tests": [
                                            ExampleNode(
                                                slug="users-fix-path-based-issues",
                                                kind="assumption-test",
                                                title="Users Fix Path-Based Issues",
                                                status="not-started",
                                                body="""## Assumption

Users can resolve validation errors when given exact paths and clear messages.

## Risk Type

Usability.

## Test

Seed three invalid graphs and observe whether users can repair them from UI messages.

## Success / Failure Signal

Success: users repair two of three seeded issues without maintainer help. Failure: messages require framework knowledge.

## Decision It Informs

Whether validation messages need richer remediation actions.""",
                                            )
                                        ],
                                        "prds": [
                                            ExampleNode(
                                                slug="validation-panel",
                                                kind="prd",
                                                title="Validation Panel",
                                                status="planned",
                                                body="""## Problem

When a graph becomes invalid, users need to know what broke and where to fix it.

## User Stories

- As an editor, I can see validation issues immediately after saving a node.
- As a maintainer, I can navigate from an issue to the relevant file.
- As an agent, I can still use CLI validation as the source of truth.

## Acceptance Criteria

- The UI displays all validation issues returned by the API.
- Each issue includes a path and message.
- Issues refresh after create, edit, and delete actions.
- The UI remains usable when the graph has multiple simultaneous issues.""",
                                            )
                                        ],
                                    },
                                ),
                            ]
                        },
                    ),
                ]
            },
        ),
        ExampleNode(
            slug="fast-first-value",
            kind="outcome",
            title="Fast First Value",
            status="discovery",
            icps=["icp.founder-product-lead", "icp.agent-native-builder"],
            body="""New users can create, understand, and discuss a useful partial graph in their first session.

## Measures

- First useful graph created in under 15 minutes.
- New users can explain the difference between outcome, opportunity, and solution after using the tool.
- At least one follow-up graph edit happens within seven days.

## Known / Unknown

- Known: a blank product graph is intimidating.
- Unknown: whether guided conversation, templates, or imported docs create faster first value.""",
            children={
                "opportunities": [
                    ExampleNode(
                        slug="blank-graph-is-intimidating",
                        kind="opportunity",
                        title="Blank Graph Is Intimidating",
                        status="discovery",
                        body="""Users know their product context but do not know how to start placing it into the framework.

## Evidence

- Users ask whether their first thought is an outcome, opportunity, or solution.
- Many teams start with a feature idea rather than a measurable outcome.

## Known / Unknown

- Known: conversation lowers the barrier to graph creation.
- Unknown: whether users trust an agent to place their raw thoughts correctly.""",
                        children={
                            "solutions": [
                                ExampleNode(
                                    slug="oe-grill-conversation",
                                    kind="solution",
                                    title="OE Grill Conversation",
                                    status="active",
                                    body="""A conversational skill challenges rough product thinking and turns it into graph-ready nodes when the user is ready.

## Product Risks

- Value: grilling may feel too intense for early users.
- Usability: the agent must know when to ask versus write.
- Feasibility: graph mutation should remain explicit and reviewable.
- Viability: this creates a strong agent-native onboarding loop.

## Assumptions

- Users benefit from being challenged before their ideas become graph nodes.
- A conversation can produce better initial structure than a form.""",
                                    children={
                                        "assumption-tests": [
                                            ExampleNode(
                                                slug="conversation-produces-better-first-graph",
                                                kind="assumption-test",
                                                title="Conversation Produces Better First Graph",
                                                status="planned",
                                                body="""## Assumption

A guided conversation produces a more coherent first graph than asking users to fill out node templates.

## Risk Type

Value and usability.

## Test

Compare first-session graphs from five users using templates and five users using the conversation.

## Success / Failure Signal

Success: conversation graphs require fewer structural corrections and users report higher clarity. Failure: users prefer templates or find the conversation slow.

## Decision It Informs

Whether conversational graph creation should be the primary onboarding path.""",
                                            )
                                        ],
                                        "prds": [
                                            ExampleNode(
                                                slug="guided-first-graph",
                                                kind="prd",
                                                title="Guided First Graph",
                                                status="draft",
                                                body="""## Problem

New users struggle to turn raw product thoughts into a valid initial graph.

## User Stories

- As a founder, I can describe my product situation conversationally.
- As an agent, I can ask targeted questions before proposing graph nodes.
- As a user, I can review proposed nodes before they are written.

## Acceptance Criteria

- The flow identifies at least one ICP, outcome, opportunity, and solution candidate.
- Proposed nodes include rationale and open questions.
- The user explicitly approves file creation.
- The resulting graph validates.""",
                                            )
                                        ],
                                    },
                                ),
                                ExampleNode(
                                    slug="example-gallery",
                                    kind="solution",
                                    title="Example Gallery",
                                    status="backlog",
                                    body="""Provide example graphs for different product stages and team types.

## Product Risks

- Value: examples may be skimmed but not used.
- Usability: examples can make the framework look heavier than it is.
- Feasibility: examples need maintenance as graph rules evolve.
- Viability: examples improve demos, docs, and UI testing.

## Assumptions

- Users understand the framework faster when they can inspect realistic graphs.
- UI development benefits from a comprehensive graph fixture.""",
                                    children={
                                        "assumption-tests": [
                                            ExampleNode(
                                                slug="examples-speed-up-understanding",
                                                kind="assumption-test",
                                                title="Examples Speed Up Understanding",
                                                status="not-started",
                                                body="""## Assumption

Inspecting realistic graphs helps users understand the framework faster than reading abstract documentation.

## Risk Type

Value and usability.

## Test

Ask new users to explain the framework after reading docs only, then after inspecting examples.

## Success / Failure Signal

Success: example users correctly classify outcomes, opportunities, solutions, assumption tests, and PRDs. Failure: examples make the framework feel heavier or more confusing.

## Decision It Informs

Whether examples should appear in onboarding or remain developer fixtures.""",
                                            )
                                        ],
                                        "prds": [
                                            ExampleNode(
                                                slug="ui-evaluation-example",
                                                kind="prd",
                                                title="UI Evaluation Example",
                                                status="backlog",
                                                body="""## Problem

UI work needs a realistic graph fixture with enough breadth and depth to reveal layout, editing, and navigation issues.

## User Stories

- As a UI developer, I can load a comprehensive graph without hand-building files.
- As a reviewer, I can inspect statuses, ICP edges, nested opportunities, PRDs, and assumption tests.
- As a maintainer, I can regenerate the fixture from the CLI.

## Acceptance Criteria

- The example includes multiple ICPs and outcomes.
- The example includes nested opportunities and mixed solution depth.
- The example includes shipped, active, planned, blocked, and backlog statuses.
- The example validates with `oe validate`.""",
                                            )
                                        ],
                                    },
                                ),
                            ]
                        },
                    ),
                    ExampleNode(
                        slug="framework-language-is-new",
                        kind="opportunity",
                        title="Framework Language Is New",
                        status="backlog",
                        body="""Outcome Engineering terms are familiar individually but unfamiliar as a connected graph model.

## Evidence

- Users conflate outcomes with solutions during early conversations.
- Assumption tests need concrete examples before users write useful ones.

## Known / Unknown

- Known: examples help.
- Unknown: whether inline education belongs in the UI or agent interaction.""",
                    ),
                ]
            },
        ),
    ]


def comprehensive_icps() -> list[ExampleNode]:
    return [
        ExampleNode(
            slug="founder-product-lead",
            kind="icp",
            title="Founder Product Lead",
            status="active",
            body="""## Who They Are

A founder or early product lead who owns product direction, customer discovery, prioritization, and delivery coordination.

## Jobs / Pains

- Needs to keep product thinking coherent while moving quickly.
- Wants a practical way to challenge feature ideas against outcomes.
- Lacks time to maintain separate strategy, discovery, and delivery artifacts.

## Why They Choose Us

- The graph gives them a single object for focus, challenge, and handoff.

## Where They Are Not A Fit

- Teams that only want project tracking and do not want to model product intent.""",
        ),
        ExampleNode(
            slug="agent-native-builder",
            kind="icp",
            title="Agent-Native Builder",
            status="active",
            body="""## Who They Are

A technical builder who already uses coding agents and wants product context to be legible to those agents.

## Jobs / Pains

- Wants agents to understand why work matters before editing code.
- Needs deterministic context that survives across agent sessions.
- Wants repo-native files rather than another SaaS workspace.

## Why They Choose Us

- The product graph is inspectable by humans, agents, CLIs, and git.

## Where They Are Not A Fit

- Builders who prefer ad hoc prompting and do not want durable product memory.""",
        ),
        ExampleNode(
            slug="agency-delivery-lead",
            kind="icp",
            title="Agency Delivery Lead",
            status="discovery",
            body="""## Who They Are

A delivery lead coordinating multiple client product streams with a small senior team.

## Jobs / Pains

- Needs shared context across client work without creating heavy process.
- Wants to show clients why certain work is recommended.
- Needs product rationale to survive handoffs between strategists and engineers.

## Why They Choose Us

- The graph makes recommendations and tradeoffs visible during client conversations.

## Where They Are Not A Fit

- Agencies that sell implementation only and do not own product discovery or prioritization.""",
        ),
        ExampleNode(
            slug="enterprise-product-ops",
            kind="icp",
            title="Enterprise Product Ops",
            status="future",
            body="""## Who They Are

A product operations leader trying to standardize how many teams connect strategy, discovery, and delivery.

## Jobs / Pains

- Needs repeatable product practice without forcing every team into the same tool stack.
- Wants better governance around assumptions, PRDs, and evidence.
- Needs visibility into where product reasoning is stale.

## Why They Choose Us

- Repo-native structure can coexist with team-specific workflows.

## Where They Are Not A Fit

- Organizations that require centralized portfolio management as the first purchase criterion.""",
        ),
    ]


def create_comprehensive_example(root: Path, force: bool) -> None:
    if root.exists():
        if not force:
            raise FileExistsError(f"{root} already exists. Re-run with --force to replace it.")
        shutil.rmtree(root)

    write_file(
        root / "VISION.md",
        """# Vision

Outcome Engineering helps teams turn product complexity into a traceable graph that humans and agents can understand, challenge, and act on.
""",
    )
    write_file(
        root / "STRATEGY.md",
        """# Strategy

```yaml
starts: 2026-06-01
ends: 2026-09-30
status: example
```

Use the visual graph editor as the adoption wedge, while keeping the filesystem graph and CLI deterministic enough for agent-native workflows.

## Strategic Pillars

- Make product intent visual enough for team review.
- Keep every important artifact traceable to outcomes and ICPs.
- Give agents deterministic commands for context, creation, validation, and critique.

## Not Now

- Full roadmap planning.
- Analytics dashboards.
- Automatic graph mutation without human review.
""",
    )
    for icp in comprehensive_icps():
        write_node(root / "icps", icp)
    for graph in comprehensive_graphs():
        write_node(root / "outcomes", graph)


def boligsiden_icps() -> list[ExampleNode]:
    return [
        ExampleNode(
            slug="active-home-buyer",
            kind="icp",
            title="Active Home Buyer",
            status="simulated",
            body="""## Who They Are

A Danish home buyer searching across apartments, villas, holiday homes, cooperative homes, and building plots.

## Jobs / Pains

- Needs to discover relevant homes quickly.
- Wants confidence that price, location, tradeoffs, and timing are understood.
- Needs alerts and saved searches to reduce missed opportunities.

## Why They Choose Us

- Boligsiden appears to aggregate homes for sale and connect search with local market context.

## Where They Are Not A Fit

- Buyers who already have a single property and only need financing advice.""",
        ),
        ExampleNode(
            slug="future-home-seller",
            kind="icp",
            title="Future Home Seller",
            status="simulated",
            body="""## Who They Are

A homeowner considering whether, when, and how to sell a Danish property.

## Jobs / Pains

- Wants to understand likely price and time-to-sale.
- Needs to compare estate agents without feeling sold to too early.
- Wants local market signals before contacting a broker.

## Why They Choose Us

- Boligsiden appears to combine public market statistics, valuation context, and broker discovery.

## Where They Are Not A Fit

- Sellers who already have a trusted estate agent and no need for market comparison.""",
        ),
        ExampleNode(
            slug="market-follower",
            kind="icp",
            title="Market Follower",
            status="simulated",
            body="""## Who They Are

A homeowner, buyer, journalist, analyst, or curious citizen tracking Danish housing-market movement.

## Jobs / Pains

- Wants reliable local price, inventory, and sales trend context.
- Needs plain-language explanations of changing housing-market conditions.
- Wants to compare municipalities, housing types, and time periods.

## Why They Choose Us

- Boligsiden publishes market data and housing-market news that can make the market more transparent.

## Where They Are Not A Fit

- Professional analysts who require raw data exports, custom modeling, or regulatory-grade datasets.""",
        ),
        ExampleNode(
            slug="estate-agent",
            kind="icp",
            title="Estate Agent",
            status="simulated",
            body="""## Who They Are

A Danish real-estate professional or chain using Boligsiden as a distribution, lead, visibility, and market-insight channel.

## Jobs / Pains

- Wants qualified buyer and seller demand.
- Needs listings to appear accurately and attractively.
- Wants market visibility that helps win mandates.

## Why They Choose Us

- Boligsiden appears to sit close to both consumer search demand and broker-facing exposure.

## Where They Are Not A Fit

- Agents who do not participate in digital listing distribution.""",
        ),
    ]


def boligsiden_graphs() -> list[ExampleNode]:
    return [
        ExampleNode(
            slug="buyer-search-confidence",
            kind="outcome",
            title="Buyer Search Confidence",
            status="simulated",
            icps=["icp.active-home-buyer"],
            body="""Home buyers trust Boligsiden enough to use it as their primary home-search workflow.

## Measures

- More buyers create saved searches and alerts.
- Buyers return to compare homes before contacting agents.
- Contact intent increases on high-fit listings.

## Known / Unknown

- Known: Boligsiden exposes listing search, map/list browsing, property detail pages, alerts, and saved homes.
- Unknown: exact conversion rates, alert performance, and which property attributes most predict contact intent.
- Simulated: all measures and opportunity sizing in this graph are estimated for UI and product-thinking evaluation.""",
            files={
                "research/source-notes.md": """# Source Notes

This graph is inferred from public Boligsiden surfaces: listing search, property detail pages, market/news content, app/search flows, and broker/contact surfaces.

Assumptions are simulated. Treat every metric and prioritization statement as a placeholder until validated with analytics, interviews, support data, and broker feedback.
""",
            },
            children={
                "opportunities": [
                    ExampleNode(
                        slug="relevant-homes-are-easy-to-miss",
                        kind="opportunity",
                        title="Relevant Homes Are Easy To Miss",
                        status="simulated",
                        body="""Buyers can miss suitable homes because geography, budget, property type, condition, open-house timing, and price changes do not fit neatly into one search.

## Evidence

- Public product surface suggests saved searches and alerts are important.
- Housing search is episodic but time-sensitive, especially in competitive areas.

## Known / Unknown

- Known: search and alert UX likely drives repeat usage.
- Unknown: whether users miss homes due to filters, ranking, alert timing, or unclear listing data.""",
                        children={
                            "solutions": [
                                ExampleNode(
                                    slug="smart-search-alerts",
                                    kind="solution",
                                    title="Smart Search Alerts",
                                    status="simulated",
                                    body="""A saved-search alert system that explains why a listing matches, highlights changed listings, and suggests safe filter expansions.

## Product Risks

- Value: buyers may already feel alerts are sufficient.
- Usability: recommendations must not feel like spam.
- Feasibility: requires matching logic over geography, price, property type, and behavioral signals.
- Viability: better alerts can increase repeat visits and agent contact volume.

## Assumptions

- Buyers value explainable alert matches.
- Slightly broader alerts catch useful homes without creating noise.""",
                                    children={
                                        "assumption-tests": [
                                            ExampleNode(
                                                slug="explainable-alerts-increase-clicks",
                                                kind="assumption-test",
                                                title="Explainable Alerts Increase Clicks",
                                                status="simulated",
                                                body="""## Assumption

Alerts that explain the match reason get more qualified clicks than generic new-listing alerts.

## Risk Type

Value and usability.

## Test

A/B test normal alerts against alerts with short match reasons and price/change badges.

## Success / Failure Signal

Success: higher click-through and saved-home rate without higher unsubscribe rate. Failure: no lift or more alert fatigue.

## Decision It Informs

Whether to invest in personalization and match explanations.""",
                                            ),
                                            ExampleNode(
                                                slug="filter-expansions-recover-missed-homes",
                                                kind="assumption-test",
                                                title="Filter Expansions Recover Missed Homes",
                                                status="simulated",
                                                body="""## Assumption

Suggesting nearby areas, flexible price bands, and adjacent property types helps buyers discover viable homes they would otherwise miss.

## Risk Type

Value.

## Test

Offer suggested expansions to users with low-result searches and measure saved homes and contact starts.

## Success / Failure Signal

Success: expanded suggestions produce meaningful saves or contacts. Failure: users dismiss suggestions as irrelevant.

## Decision It Informs

How aggressive the search-assist experience should be.""",
                                            ),
                                        ],
                                        "prds": [
                                            ExampleNode(
                                                slug="smart-alerts-mvp",
                                                kind="prd",
                                                title="Smart Alerts MVP",
                                                status="simulated",
                                                body="""## Problem

Buyers need to know quickly when a relevant home appears or changes, but broad searches create noise and narrow searches miss homes.

## User Stories

- As a buyer, I can save a search and receive alerts with clear match reasons.
- As a buyer, I can see price drops and open-house updates in alerts.
- As a buyer, I can add a suggested nearby area or adjusted price range.

## Acceptance Criteria

- Alerts include property type, area, price, and change reason.
- Users can tune frequency and criteria from the alert.
- Suggested expansions are shown only for low-result or low-engagement searches.
- Alert interactions are measurable end to end.""",
                                            )
                                        ],
                                    },
                                ),
                                ExampleNode(
                                    slug="neighborhood-watchlist",
                                    kind="solution",
                                    title="Neighborhood Watchlist",
                                    status="simulated",
                                    body="""Let buyers follow neighborhoods or postal codes before they are ready to define a precise property search.

## Product Risks

- Value: users may prefer property alerts over area alerts.
- Usability: area updates must be concise and actionable.
- Feasibility: neighborhood boundaries and local stats can be fuzzy.
- Viability: watchlists create earlier buyer relationships.

## Assumptions

- Buyers often choose areas before they choose exact property criteria.
- Area-level updates can bring users back before new relevant listings appear.""",
                                    children={
                                        "assumption-tests": [
                                            ExampleNode(
                                                slug="area-watchlists-capture-early-buyers",
                                                kind="assumption-test",
                                                title="Area Watchlists Capture Early Buyers",
                                                status="simulated",
                                                body="""## Assumption

Area watchlists attract buyers earlier than saved property searches.

## Risk Type

Value.

## Test

Offer area watchlists from local context pages and compare subsequent search creation, saved homes, and contact starts.

## Success / Failure Signal

Success: area followers later create searches or save homes at a meaningful rate. Failure: watchlists become passive subscriptions.

## Decision It Informs

Whether Boligsiden should invest in pre-search buyer journeys.""",
                                            )
                                        ],
                                        "prds": [
                                            ExampleNode(
                                                slug="neighborhood-watchlist-mvp",
                                                kind="prd",
                                                title="Neighborhood Watchlist MVP",
                                                status="simulated",
                                                body="""## Problem

Buyers often care about an area before they know exact property criteria, but listing alerts require defined searches.

## User Stories

- As a buyer, I can follow a postal code, municipality, or neighborhood.
- As a buyer, I can receive notable local changes and new listings.
- As a buyer, I can convert an area watchlist into a saved search.

## Acceptance Criteria

- Users can follow an area from maps, listings, and local context pages.
- Updates include new listings, price movement, and market-stat changes.
- Users can tune frequency.
- Watchlists link to search creation and saved homes.""",
                                            )
                                        ],
                                    },
                                ),
                            ]
                        },
                    ),
                    ExampleNode(
                        slug="property-tradeoffs-are-hard-to-compare",
                        kind="opportunity",
                        title="Property Tradeoffs Are Hard To Compare",
                        status="simulated",
                        body="""Buyers compare homes across price, square meters, energy, location, days on market, price changes, and subjective fit, but listings are often evaluated one at a time.

## Evidence

- Public listing pages expose many structured attributes.
- Buyers naturally shortlist homes and compare tradeoffs before contacting agents.

## Known / Unknown

- Known: comparison work exists.
- Unknown: whether users want a formal comparison board or lighter saved-home summaries.""",
                        children={
                            "solutions": [
                                ExampleNode(
                                    slug="shortlist-comparison-board",
                                    kind="solution",
                                    title="Shortlist Comparison Board",
                                    status="simulated",
                                    body="""A saved-home comparison view that shows property attributes, local context, price movement, and next action side by side.

## Product Risks

- Value: comparison may happen outside the product in spreadsheets or family chats.
- Usability: side-by-side comparison must work on mobile.
- Feasibility: attribute completeness varies across listings.
- Viability: comparison can deepen engagement before contact.

## Assumptions

- Buyers save multiple homes before contacting agents.
- Structured comparison increases confidence and reduces indecision.""",
                                    children={
                                        "assumption-tests": [
                                            ExampleNode(
                                                slug="comparison-increases-return-visits",
                                                kind="assumption-test",
                                                title="Comparison Increases Return Visits",
                                                status="simulated",
                                                body="""## Assumption

Buyers who can compare saved homes return more often and contact agents with more confidence.

## Risk Type

Value.

## Test

Release comparison to a percentage of signed-in saved-home users and measure return sessions, notes, shares, and contact starts.

## Success / Failure Signal

Success: higher return sessions and contact intent. Failure: low comparison usage.

## Decision It Informs

Whether comparison should be a core buyer workflow.""",
                                            )
                                        ],
                                        "prds": [
                                            ExampleNode(
                                                slug="saved-home-comparison",
                                                kind="prd",
                                                title="Saved Home Comparison",
                                                status="simulated",
                                                body="""## Problem

Buyers need a simple way to compare saved homes and decide which properties deserve action.

## User Stories

- As a buyer, I can select saved homes and compare key attributes.
- As a buyer, I can see price changes, days on market, and monthly cost estimates.
- As a buyer, I can mark homes as reject, maybe, or contact.

## Acceptance Criteria

- Comparison supports at least two and up to six homes.
- The mobile layout remains readable.
- Missing attributes are clearly shown as unknown.
- Users can start contact or book viewing from comparison.""",
                                            )
                                        ],
                                    },
                                ),
                                ExampleNode(
                                    slug="monthly-cost-context",
                                    kind="solution",
                                    title="Monthly Cost Context",
                                    status="simulated",
                                    body="""Show estimated monthly cost ranges and affordability notes beside listing price.

## Product Risks

- Value: users may already rely on bank calculators.
- Usability: estimates must be clearly approximate.
- Feasibility: financing rules and rates change.
- Viability: affordability context may reduce low-quality contacts.

## Assumptions

- Buyers need more than asking price to assess affordability.
- Approximate ranges are useful if uncertainty is explicit.""",
                                ),
                            ]
                        },
                    ),
                    ExampleNode(
                        slug="local-area-confidence-is-fragile",
                        kind="opportunity",
                        title="Local Area Confidence Is Fragile",
                        status="simulated",
                        body="""Buyers need to understand neighborhoods, commute, schools, noise, prices, and local market movement before acting on a home.

## Evidence

- Market transparency and local statistics appear central to Boligsiden's public proposition.
- Location confidence is a common home-buying blocker.

## Known / Unknown

- Known: listing fit depends strongly on area fit.
- Unknown: which local signals most affect Danish buyer confidence.""",
                        children={
                            "solutions": [
                                ExampleNode(
                                    slug="local-context-panel",
                                    kind="solution",
                                    title="Local Context Panel",
                                    status="simulated",
                                    body="""A property-detail module that combines local sales prices, inventory, time-on-market, transport, and similar homes.

## Product Risks

- Value: users may prefer maps over data panels.
- Usability: too much data can distract from the listing.
- Feasibility: some local data may be sparse.
- Viability: local context differentiates Boligsiden from pure listing feeds.

## Assumptions

- Local trend context increases buyer confidence.
- Showing similar sold homes helps buyers judge asking price.""",
                                    children={
                                        "assumption-tests": [
                                            ExampleNode(
                                                slug="sold-comps-build-price-confidence",
                                                kind="assumption-test",
                                                title="Sold Comparables Build Price Confidence",
                                                status="simulated",
                                                body="""## Assumption

Showing relevant sold comparables makes buyers more confident about whether the asking price is reasonable.

## Risk Type

Value and trust.

## Test

Prototype a local context panel and ask buyers to evaluate three listings with and without sold comparables.

## Success / Failure Signal

Success: buyers explain price confidence more clearly and take next action faster. Failure: comps confuse users or feel inapplicable.

## Decision It Informs

Whether sold comparables should be prominent on listing pages.""",
                                            )
                                        ],
                                        "prds": [
                                            ExampleNode(
                                                slug="property-local-context",
                                                kind="prd",
                                                title="Property Local Context",
                                                status="simulated",
                                                body="""## Problem

Buyers cannot easily tell whether a home's price and location make sense relative to the local market.

## User Stories

- As a buyer, I can see local price trends near a listing.
- As a buyer, I can compare the listing to similar sold homes.
- As a buyer, I can see nearby active alternatives.

## Acceptance Criteria

- The module appears on property detail pages.
- It separates sold comparables, active alternatives, and area trends.
- Sparse data states are clear and non-misleading.
- Users can save, share, or contact from the module.""",
                                            )
                                        ],
                                    },
                                )
                            ]
                        },
                    ),
                ]
            },
        ),
        ExampleNode(
            slug="seller-market-readiness",
            kind="outcome",
            title="Seller Market Readiness",
            status="simulated",
            icps=["icp.future-home-seller", "icp.estate-agent"],
            body="""Homeowners use Boligsiden to understand their sale opportunity and take the next step toward a qualified agent conversation.

## Measures

- More homeowners view local sales and valuation content.
- Seller-intent actions increase, such as agent comparison or contact requests.
- Estate agents receive better-qualified seller leads.

## Known / Unknown

- Known: Boligsiden has public surfaces around agents and market data.
- Unknown: the commercial model and exact seller lead flows.
- Simulated: this outcome assumes seller readiness is strategically valuable because it bridges consumer data and broker demand.""",
            children={
                "opportunities": [
                    ExampleNode(
                        slug="sellers-do-not-know-when-to-act",
                        kind="opportunity",
                        title="Sellers Do Not Know When To Act",
                        status="simulated",
                        body="""Potential sellers struggle to judge whether local demand, price movement, and inventory make it a good time to sell.

## Evidence

- Housing-market news and statistics suggest demand for market interpretation.
- Sellers often need confidence before contacting an estate agent.

## Known / Unknown

- Known: timing and expected price matter to sellers.
- Unknown: whether sellers want self-serve guidance or human follow-up quickly.""",
                        children={
                            "solutions": [
                                ExampleNode(
                                    slug="seller-readiness-score",
                                    kind="solution",
                                    title="Seller Readiness Score",
                                    status="simulated",
                                    body="""A local-market readiness summary that combines recent sales, price trends, active supply, time-on-market, and demand indicators for the seller's area and property type.

## Product Risks

- Value: sellers may distrust a score without human context.
- Usability: scores can oversimplify an emotional financial decision.
- Feasibility: data coverage varies by area and property type.
- Viability: readiness context can create qualified agent leads.

## Assumptions

- Sellers want a private, self-serve first read before contacting agents.
- A score plus explanation performs better than raw market statistics.""",
                                    children={
                                        "assumption-tests": [
                                            ExampleNode(
                                                slug="readiness-score-creates-agent-intent",
                                                kind="assumption-test",
                                                title="Readiness Score Creates Agent Intent",
                                                status="simulated",
                                                body="""## Assumption

Sellers who receive a local readiness explanation are more likely to request agent contact.

## Risk Type

Value and viability.

## Test

Offer readiness summaries to market-statistics visitors and measure agent-comparison or contact starts.

## Success / Failure Signal

Success: higher seller-intent conversion with no increase in low-quality leads. Failure: users consume the score but do not act.

## Decision It Informs

Whether to build seller guidance as a conversion path.""",
                                            )
                                        ],
                                        "prds": [
                                            ExampleNode(
                                                slug="seller-readiness-mvp",
                                                kind="prd",
                                                title="Seller Readiness MVP",
                                                status="simulated",
                                                body="""## Problem

Potential sellers need a clear first read on local market conditions before they are ready to contact an agent.

## User Stories

- As a homeowner, I can enter my property type and area.
- As a homeowner, I can see a plain-language market readiness summary.
- As a homeowner, I can request agent advice when ready.

## Acceptance Criteria

- The summary includes recent sales, active supply, price trend, and uncertainty.
- The output avoids guaranteed price claims.
- Users can proceed to agent comparison.
- Lead quality can be measured after handoff.""",
                                            )
                                        ],
                                    },
                                ),
                                ExampleNode(
                                    slug="listing-prep-checklist",
                                    kind="solution",
                                    title="Listing Prep Checklist",
                                    status="simulated",
                                    body="""A seller checklist that helps homeowners prepare core information before requesting agent advice.

## Product Risks

- Value: sellers may want immediate human contact instead of preparation.
- Usability: checklist must not feel like work before value.
- Feasibility: useful prep depends on property type and seller stage.
- Viability: better-prepared sellers can improve lead quality for agents.

## Assumptions

- Sellers are willing to answer a few prep questions if they receive better advice.
- Agent leads with structured property context convert better.""",
                                    children={
                                        "assumption-tests": [
                                            ExampleNode(
                                                slug="prep-checklist-improves-leads",
                                                kind="assumption-test",
                                                title="Prep Checklist Improves Leads",
                                                status="simulated",
                                                body="""## Assumption

Seller leads with prep checklist context are more valuable to estate agents than bare contact requests.

## Risk Type

Value and viability.

## Test

Send a subset of seller leads with checklist context and ask agents to rate usefulness after first contact.

## Success / Failure Signal

Success: agents rate checklist leads as more prepared and more likely to become mandates. Failure: checklist completion reduces lead volume too much.

## Decision It Informs

Whether seller preparation should sit before or after agent contact.""",
                                            )
                                        ],
                                        "prds": [
                                            ExampleNode(
                                                slug="seller-prep-checklist",
                                                kind="prd",
                                                title="Seller Prep Checklist",
                                                status="simulated",
                                                body="""## Problem

Sellers and agents need better context before the first valuation or advice conversation.

## User Stories

- As a seller, I can answer a few property and timing questions.
- As a seller, I can see what information helps agents advise me.
- As an agent, I receive seller context before making contact.

## Acceptance Criteria

- The checklist captures property type, timing, motivation, known improvements, and preferred contact path.
- Sellers can skip optional questions.
- Checklist context is included in agent handoff.
- Completion and lead-quality effects are measured.""",
                                            )
                                        ],
                                    },
                                ),
                            ]
                        },
                    ),
                    ExampleNode(
                        slug="agent-choice-feels-opaque",
                        kind="opportunity",
                        title="Agent Choice Feels Opaque",
                        status="simulated",
                        body="""Sellers need to choose an estate agent, but may not know how to compare local experience, fit, and likely sale strategy.

## Evidence

- Boligsiden appears to include broker/agent discovery surfaces.
- Seller decisions depend on trust, local track record, and service fit.

## Known / Unknown

- Known: broker comparison is a natural seller job.
- Unknown: what broker performance data can be shown fairly and commercially.""",
                        children={
                            "solutions": [
                                ExampleNode(
                                    slug="agent-fit-comparison",
                                    kind="solution",
                                    title="Agent Fit Comparison",
                                    status="simulated",
                                    body="""A seller-facing comparison of local agents by recent nearby activity, property-type experience, customer signals, and next available consultation.

## Product Risks

- Value: sellers may still choose based on personal recommendations.
- Usability: comparison must feel fair and not like ads only.
- Feasibility: performance data and review signals may be incomplete.
- Viability: agent visibility must align with broker relationships.

## Assumptions

- Sellers want structured comparison before requesting a valuation.
- Estate agents will accept transparent fit signals if lead quality improves.""",
                                    children={
                                        "assumption-tests": [
                                            ExampleNode(
                                                slug="fit-signals-improve-lead-quality",
                                                kind="assumption-test",
                                                title="Fit Signals Improve Lead Quality",
                                                status="simulated",
                                                body="""## Assumption

Showing why an agent is a good fit increases seller lead quality and broker acceptance.

## Risk Type

Value and viability.

## Test

Compare leads from a simple contact form with leads from a fit-comparison flow.

## Success / Failure Signal

Success: higher broker-rated quality and seller completion rate. Failure: sellers do not use comparison or brokers dislike ranking signals.

## Decision It Informs

How transparent the agent comparison product should become.""",
                                            )
                                        ],
                                        "prds": [
                                            ExampleNode(
                                                slug="agent-fit-comparison-mvp",
                                                kind="prd",
                                                title="Agent Fit Comparison MVP",
                                                status="simulated",
                                                body="""## Problem

Sellers need to compare local estate agents before asking for valuation or sales advice.

## User Stories

- As a seller, I can compare local agents by relevant local experience.
- As a seller, I can request contact from one or more agents.
- As an agent, I receive context about the seller's property and needs.

## Acceptance Criteria

- Agent cards show local activity, property-type relevance, and service area.
- Sponsored or commercial placements are clearly distinguished if present.
- Sellers can request contact without retyping property basics.
- Broker feedback can mark lead quality after contact.""",
                                            )
                                        ],
                                    },
                                )
                            ]
                        },
                    ),
                ]
            },
        ),
        ExampleNode(
            slug="market-transparency-trust",
            kind="outcome",
            title="Market Transparency Trust",
            status="simulated",
            icps=["icp.market-follower", "icp.active-home-buyer", "icp.future-home-seller"],
            body="""Consumers and market followers trust Boligsiden as a clear, current, and explainable source for Danish housing-market insight.

## Measures

- More users visit market-statistics and news surfaces repeatedly.
- Users move from market insight to search, saved homes, seller readiness, or agent comparison.
- Press and public discourse cite Boligsiden insights.

## Known / Unknown

- Known: Boligsiden publicly presents housing-market statistics and news.
- Unknown: which market-insight formats drive product actions versus passive readership.
- Simulated: this outcome assumes transparency is both a brand and conversion lever.""",
            files={
                "research/public-product-observations.md": """# Public Product Observations

- Boligsiden appears to combine live property search with market data, news, broker discovery, and consumer guidance.
- Strong graph opportunities likely sit where market transparency changes a buyer or seller decision.
- Internal analytics would be needed to rank these opportunities.
""",
            },
            children={
                "opportunities": [
                    ExampleNode(
                        slug="market-data-is-hard-to-interpret",
                        kind="opportunity",
                        title="Market Data Is Hard To Interpret",
                        status="simulated",
                        body="""Raw housing-market numbers can be difficult for consumers to translate into decisions about buying, selling, or waiting.

## Evidence

- Public news and statistics suggest Boligsiden already invests in market explanation.
- Consumers need local, property-type-specific interpretation rather than national averages only.

## Known / Unknown

- Known: market context matters.
- Unknown: whether users prefer articles, charts, explainers, alerts, or embedded listing context.""",
                        children={
                            "solutions": [
                                ExampleNode(
                                    slug="local-market-briefings",
                                    kind="solution",
                                    title="Local Market Briefings",
                                    status="simulated",
                                    body="""Personalized local market briefings for a municipality, postal code, or saved-search area.

## Product Risks

- Value: market followers may read without taking action.
- Usability: briefings must avoid false precision.
- Feasibility: local explanations need robust templating and editorial guardrails.
- Viability: briefings can re-engage buyers, sellers, and press readers.

## Assumptions

- Local explanations drive more action than national market updates.
- Users will subscribe to market updates for areas they care about.""",
                                    children={
                                        "assumption-tests": [
                                            ExampleNode(
                                                slug="local-briefings-drive-return",
                                                kind="assumption-test",
                                                title="Local Briefings Drive Return",
                                                status="simulated",
                                                body="""## Assumption

Users who subscribe to local market briefings return more often and perform more buyer or seller actions.

## Risk Type

Value.

## Test

Launch email or in-product briefings for saved areas and compare retention plus downstream actions against a control group.

## Success / Failure Signal

Success: higher return rate and meaningful downstream search or seller actions. Failure: readership does not translate into product usage.

## Decision It Informs

Whether market insight should become personalized and subscription-based.""",
                                            )
                                        ],
                                        "prds": [
                                            ExampleNode(
                                                slug="local-market-briefing-mvp",
                                                kind="prd",
                                                title="Local Market Briefing MVP",
                                                status="simulated",
                                                body="""## Problem

Users need housing-market interpretation for the specific areas and property types they care about.

## User Stories

- As a buyer, I can follow market movement in my saved-search area.
- As a seller, I can follow demand and supply in my local area.
- As a market follower, I can understand why prices or inventory changed.

## Acceptance Criteria

- Users can subscribe to one or more local areas.
- Briefings include price trend, inventory, time-on-market, and explanation.
- Data sparsity and uncertainty are visible.
- Briefings link to relevant listings, seller guidance, or agent discovery.""",
                                            )
                                        ],
                                    },
                                )
                            ]
                        },
                    ),
                    ExampleNode(
                        slug="data-freshness-is-invisible",
                        kind="opportunity",
                        title="Data Freshness Is Invisible",
                        status="simulated",
                        body="""Users may not know when listings, price changes, sold data, or statistics were last updated, which can reduce trust in a fast-moving market.

## Evidence

- Listing and market data products depend on freshness.
- Trust issues are amplified when users act on expensive decisions.

## Known / Unknown

- Known: freshness affects confidence.
- Unknown: whether explicit freshness badges increase trust or clutter the interface.""",
                        children={
                            "solutions": [
                                ExampleNode(
                                    slug="freshness-and-source-badges",
                                    kind="solution",
                                    title="Freshness And Source Badges",
                                    status="simulated",
                                    body="""Show clear update timestamps, source explanations, and confidence states on listings and market-data modules.

## Product Risks

- Value: users may not notice freshness details.
- Usability: badges can add noise.
- Feasibility: source and update semantics may vary by data type.
- Viability: visible trust signals can defend brand credibility.

## Assumptions

- Freshness indicators increase trust on high-intent pages.
- Users prefer transparent uncertainty to silent missing data.""",
                                    children={
                                        "assumption-tests": [
                                            ExampleNode(
                                                slug="freshness-badges-improve-trust",
                                                kind="assumption-test",
                                                title="Freshness Badges Improve Trust",
                                                status="simulated",
                                                body="""## Assumption

Visible data freshness and source badges increase user trust without reducing task completion.

## Risk Type

Usability and trust.

## Test

Show badges on selected market modules and survey perceived trust while measuring click and contact behavior.

## Success / Failure Signal

Success: trust improves with no task-completion drop. Failure: badges add clutter or raise more doubts.

## Decision It Informs

How explicit source and freshness metadata should be in the UI.""",
                                            )
                                        ],
                                        "prds": [
                                            ExampleNode(
                                                slug="data-freshness-indicators",
                                                kind="prd",
                                                title="Data Freshness Indicators",
                                                status="simulated",
                                                body="""## Problem

Users need to know how current listing and market data is before acting on it.

## User Stories

- As a buyer, I can see whether a listing price or open-house detail was recently updated.
- As a seller, I can understand the age of local market statistics.
- As a market follower, I can see where data comes from.

## Acceptance Criteria

- Listings and market modules expose update recency.
- Source language is concise and understandable.
- Unknown or stale data states are explicit.
- Badges do not obscure primary calls to action.""",
                                            )
                                        ],
                                    },
                                )
                            ]
                        },
                    ),
                    ExampleNode(
                        slug="insight-does-not-connect-to-action",
                        kind="opportunity",
                        title="Insight Does Not Connect To Action",
                        status="simulated",
                        body="""A user may read a market article or statistic but not understand what to do next as a buyer, seller, or observer.

## Evidence

- Market insight can be editorially valuable without driving product movement.
- Boligsiden's unique position is stronger if insight connects to search, seller readiness, and agent discovery.

## Known / Unknown

- Known: action pathways can make content more useful.
- Unknown: which next action is appropriate for each article or data view.""",
                        children={
                            "solutions": [
                                ExampleNode(
                                    slug="insight-to-action-modules",
                                    kind="solution",
                                    title="Insight To Action Modules",
                                    status="simulated",
                                    body="""Contextual next-step modules on articles and market-stat pages, such as follow this area, view homes, estimate sale readiness, or compare agents.

## Product Risks

- Value: readers may not want transactional prompts inside editorial content.
- Usability: CTAs must fit the user's likely intent.
- Feasibility: content taxonomy must map to buyer, seller, or market-follower actions.
- Viability: connects brand trust to measurable product outcomes.

## Assumptions

- Relevant next-step prompts help users act on market insight.
- Intent-specific modules outperform generic listing-search CTAs.""",
                                    children={
                                        "assumption-tests": [
                                            ExampleNode(
                                                slug="intent-specific-ctas-outperform-generic",
                                                kind="assumption-test",
                                                title="Intent-Specific CTAs Outperform Generic",
                                                status="simulated",
                                                body="""## Assumption

Buyer, seller, and market-follower CTAs tailored to article context outperform generic search prompts.

## Risk Type

Value.

## Test

Classify selected market articles by intent and compare contextual modules against generic search modules.

## Success / Failure Signal

Success: higher follow-area, search, seller, or agent actions. Failure: CTAs distract from content or do not move downstream behavior.

## Decision It Informs

Whether market content should become a product acquisition surface.""",
                                            )
                                        ],
                                        "prds": [
                                            ExampleNode(
                                                slug="market-insight-next-actions",
                                                kind="prd",
                                                title="Market Insight Next Actions",
                                                status="simulated",
                                                body="""## Problem

Market readers need clear, relevant next actions after learning something about an area or market condition.

## User Stories

- As a buyer, I can jump from an area insight to relevant homes.
- As a seller, I can move from a local-market article to seller readiness.
- As a market follower, I can follow future updates for the area.

## Acceptance Criteria

- Each module is mapped to article or statistic intent.
- Modules can be suppressed on content where action would feel inappropriate.
- Clicks and downstream actions are tracked.
- Editorial content remains readable and credible.""",
                                            )
                                        ],
                                    },
                                )
                            ]
                        },
                    ),
                ]
            },
        ),
    ]


def create_boligsiden_example(root: Path, force: bool) -> None:
    if root.exists():
        if not force:
            raise FileExistsError(f"{root} already exists. Re-run with --force to replace it.")
        shutil.rmtree(root)

    write_file(
        root / "VISION.md",
        """# Vision

Boligsiden helps people make confident Danish housing decisions by connecting property search, market transparency, seller guidance, and estate-agent discovery.

This is a simulated product graph based only on public product research. It is meant for UI evaluation and product-thinking practice, not as a claim about Boligsiden's actual internal strategy.
""",
    )
    write_file(
        root / "STRATEGY.md",
        """# Strategy

```yaml
starts: 2026-07-01
ends: 2026-12-31
status: simulated
```

Use Boligsiden's public strengths in listing search, housing-market data, and broker connection to become the most trusted decision surface for Danish buyers and sellers.

## Strategic Pillars

- Make search smarter and more confidence-building for buyers.
- Turn market data into actionable seller and buyer guidance.
- Connect insight to qualified estate-agent and property actions.
- Preserve trust through transparent freshness, uncertainty, and source signals.

## Research Boundary

This graph is inferred from public Boligsiden surfaces and general housing-market product logic. All metrics, opportunity sizing, priorities, and solution economics are simulated.

## Not Now

- Replacing bank financing advice.
- Owning the full estate-agent workflow.
- Building raw-data tools for professional analysts before consumer decision flows.
""",
    )
    write_file(
        root / "RESEARCH.md",
        """# Research Notes

Publicly observed product areas:

- Property search and listing detail pages.
- Saved searches, alerts, and app-style recurring buyer workflows.
- Market statistics, housing-market news, and local data storytelling.
- Estate-agent discovery or contact paths.

Important caveat: this graph estimates product opportunities from outside the company. Internal analytics, user interviews, broker economics, and data contracts could substantially change priorities.
""",
    )
    for icp in boligsiden_icps():
        write_node(root / "icps", icp)
    for graph in boligsiden_graphs():
        write_node(root / "outcomes", graph)


def create_example(root: Path, force: bool, comprehensive: bool = False, boligsiden: bool = False) -> None:
    if comprehensive and boligsiden:
        raise ValueError("choose either comprehensive or boligsiden, not both")
    if comprehensive:
        create_comprehensive_example(root, force)
        return
    if boligsiden:
        create_boligsiden_example(root, force)
        return

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
    for icp in example_icps():
        write_node(root / "icps", icp)
    write_node(root / "outcomes", example_graph())
