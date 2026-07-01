from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


MARKER_FILES = {
    "VISION.md": "vision",
    "STRATEGY.md": "strategy",
    "ICP.md": "icp",
    "OUTCOME.md": "outcome",
    "OPPORTUNITY.md": "opportunity",
    "SOLUTION.md": "solution",
    "ASSUMPTION_TEST.md": "assumption-test",
    "PRD.md": "prd",
}

FLYWHEEL_COLLECTION = "flywheels"
FLYWHEEL_MARKER_FILE = "FLYWHEEL.md"
FLYWHEEL_NODE_MARKER_FILE = "FLYWHEEL_NODE.md"
FLYWHEEL_KIND = "flywheel"
FLYWHEEL_NODE_KIND = "flywheel-node"

RELATIONSHIP_TO_CHILD_KIND = {
    "strategies": {"strategy"},
    "outcomes": {"outcome"},
    "opportunities": {"opportunity"},
    "solutions": {"solution"},
    "assumption-tests": {"assumption-test"},
    "prds": {"prd"},
}

RELATIONSHIP_ORDER = ("strategies", "outcomes", "opportunities", "solutions", "assumption-tests", "prds")

# An ICP (Ideal Customer Profile) is the "who" the graph serves. It is not a step
# in the outcome -> opportunity -> solution trace chain, so it does not nest under
# another node. Instead ICPs live in a top-level collection and outcomes and
# opportunities point at them by id through the ICP_REFERENCE_FIELD. This keeps the
# many-to-many reality (one ICP serves many outcomes, one outcome serves many ICPs)
# without breaking the strict tree the trace chain relies on.
ICP_COLLECTION = "icps"
ICP_KIND = "icp"
ICP_REFERENCE_FIELD = "icps"
ICP_REFERRING_KINDS = {"outcome", "opportunity"}
STRATEGY_COLLECTION = "strategies"
STRATEGY_KIND = "strategy"

# Node kinds that live directly under the graph root rather than under a parent node.
ROOT_KINDS = {"strategy", "outcome", "icp"}

KIND_TO_MARKER_FILE = {kind: marker for marker, kind in MARKER_FILES.items()}

KIND_TO_RELATIONSHIP = {
    "strategy": "strategies",
    "icp": "icps",
    "outcome": "outcomes",
    "opportunity": "opportunities",
    "solution": "solutions",
    "assumption-test": "assumption-tests",
    "prd": "prds",
}

PARENT_KIND_TO_CHILD_KIND = {
    "root": {"strategy", "outcome", "icp"},
    "outcome": {"opportunity"},
    "opportunity": {"opportunity", "solution"},
    "solution": {"assumption-test", "prd"},
}

ALLOWED_CHILD_RELATIONSHIPS = {
    "root": {"strategies", "outcomes"},
    "vision": set(),
    "strategy": set(),
    "icp": set(),
    "outcome": {"opportunities"},
    "opportunity": {"opportunities", "solutions"},
    "solution": {"assumption-tests", "prds"},
    "assumption-test": set(),
    "prd": set(),
}


@dataclass(frozen=True)
class ProductNode:
    path: Path
    kind: str
    marker_file: Path
    slug: str
    parent: "ProductNode | None" = None
    relationship: str | None = None
    children: list["ProductNode"] = field(default_factory=list)

    @property
    def id(self) -> str:
        return f"{self.kind}.{self.slug}"


@dataclass(frozen=True)
class FlywheelNode:
    path: Path
    marker_file: Path
    slug: str
    title: str
    body: str
    status: str | None
    next: list[str]

    @property
    def id(self) -> str:
        return f"{FLYWHEEL_NODE_KIND}.{self.slug}"


@dataclass(frozen=True)
class FlywheelGraph:
    path: Path
    marker_file: Path
    slug: str
    title: str
    body: str
    status: str | None
    nodes: list[FlywheelNode]

    @property
    def id(self) -> str:
        return f"{FLYWHEEL_KIND}.{self.slug}"


@dataclass(frozen=True)
class ValidationIssue:
    path: Path
    message: str
