from __future__ import annotations

import os
import shutil
from importlib import resources
from pathlib import Path


SKILL_NAME = "oe-cli"


def skill_target(agent: str) -> Path:
    normalized = agent.lower()
    if normalized == "codex":
        return codex_skill_target()
    if normalized == "claude":
        return claude_skill_target()
    raise ValueError(f"unsupported agent {agent!r}; expected codex, claude, or all")


def codex_skill_target() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home) / "skills" / SKILL_NAME
    return Path.home() / ".codex" / "skills" / SKILL_NAME


def claude_skill_target() -> Path:
    claude_home = os.environ.get("CLAUDE_HOME")
    if claude_home:
        return Path(claude_home) / "skills" / SKILL_NAME
    return Path.home() / ".claude" / "skills" / SKILL_NAME


def install_skill(target: Path | None = None, force: bool = False) -> Path:
    destination = (target or codex_skill_target()).expanduser()
    return copy_skill(destination, force=force)


def install_skill_for_agent(agent: str, force: bool = False) -> list[Path]:
    normalized = agent.lower()
    if normalized == "all":
        return [copy_skill(skill_target(name), force=force) for name in ("codex", "claude")]
    return [copy_skill(skill_target(normalized), force=force)]


def copy_skill(destination: Path, force: bool = False) -> Path:
    destination = destination.expanduser()
    source = resources.files("outcome_engineering") / "skills" / SKILL_NAME

    if destination.exists():
        if not force:
            raise FileExistsError(f"{destination} already exists. Re-run with --force to replace it.")
        if destination.is_dir():
            shutil.rmtree(destination)
        else:
            destination.unlink()

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)
    return destination
