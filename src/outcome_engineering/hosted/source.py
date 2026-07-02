"""Deployment source metadata for hosted API responses.

Environment-derived, so it lives at the app boundary rather than in the
product graph core.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import os
from pathlib import Path


@dataclass(frozen=True)
class SourceMetadata:
    root: str
    branch: str
    commit: str
    generated_at: str

    @classmethod
    def from_root(cls, root: Path) -> "SourceMetadata":
        return cls(
            root=str(root.resolve()),
            branch=os.environ.get("OE_SOURCE_BRANCH") or os.environ.get("SOURCE_BRANCH") or "unknown",
            commit=os.environ.get("OE_SOURCE_COMMIT")
            or os.environ.get("SOURCE_COMMIT")
            or os.environ.get("GITHUB_SHA")
            or "unknown",
            generated_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        )

    def to_dict(self) -> dict:
        return {
            "root": self.root,
            "branch": self.branch,
            "commit": self.commit,
            "generatedAt": self.generated_at,
        }


def source_dict(root: Path) -> dict:
    return SourceMetadata.from_root(root).to_dict()
