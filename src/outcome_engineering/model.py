from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


MARKER_FILES = {
    "VISION.md": "vision",
    "STRATEGY.md": "strategy",
    "OUTCOME.md": "outcome",
    "OPPORTUNITY.md": "opportunity",
    "SOLUTION.md": "solution",
    "ASSUMPTION.md": "assumption",
    "EXPERIMENT.md": "experiment",
    "PRD.md": "prd",
}

RELATIONSHIP_TO_CHILD_KIND = {
    "outcomes": {"outcome"},
    "opportunities": {"opportunity"},
    "solutions": {"solution"},
    "assumptions": {"assumption"},
    "experiments": {"experiment"},
    "prds": {"prd"},
}

ALLOWED_CHILD_RELATIONSHIPS = {
    "root": {"outcomes"},
    "vision": set(),
    "strategy": set(),
    "outcome": {"opportunities"},
    "opportunity": {"opportunities", "solutions"},
    "solution": {"assumptions", "prds"},
    "assumption": {"experiments"},
    "experiment": set(),
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

