from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


MARKER_FILES = {
    "VISION.md": "vision",
    "STRATEGY.md": "strategy",
    "OUTCOME.md": "outcome",
    "OPPORTUNITY.md": "opportunity",
    "SOLUTION.md": "solution",
    "ASSUMPTION_TEST.md": "assumption-test",
    "PRD.md": "prd",
}

RELATIONSHIP_TO_CHILD_KIND = {
    "outcomes": {"outcome"},
    "opportunities": {"opportunity"},
    "solutions": {"solution"},
    "assumption-tests": {"assumption-test"},
    "prds": {"prd"},
}

RELATIONSHIP_ORDER = ("outcomes", "opportunities", "solutions", "assumption-tests", "prds")

KIND_TO_MARKER_FILE = {kind: marker for marker, kind in MARKER_FILES.items()}

KIND_TO_RELATIONSHIP = {
    "outcome": "outcomes",
    "opportunity": "opportunities",
    "solution": "solutions",
    "assumption-test": "assumption-tests",
    "prd": "prds",
}

PARENT_KIND_TO_CHILD_KIND = {
    "root": {"outcome"},
    "outcome": {"opportunity"},
    "opportunity": {"opportunity", "solution"},
    "solution": {"assumption-test", "prd"},
}

ALLOWED_CHILD_RELATIONSHIPS = {
    "root": {"outcomes"},
    "vision": set(),
    "strategy": set(),
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
class ValidationIssue:
    path: Path
    message: str
