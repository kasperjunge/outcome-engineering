from __future__ import annotations

from pathlib import Path

import typer

from outcome_engineering.example import create_example
from outcome_engineering.graph import (
    create_node,
    discover_nodes,
    find_node,
    find_nodes_by_kind,
    marker_content,
    node_ancestors,
    supporting_files,
    validate as validate_graph,
)
from outcome_engineering.model import KIND_TO_RELATIONSHIP
from outcome_engineering.skill_installer import (
    install_project_skills,
    install_skill,
    install_skills_for_agent,
)

app = typer.Typer(help="Outcome Engineering product graph tooling.")


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def install(
    ctx: typer.Context,
    force: bool = typer.Option(False, "--force", help="Replace the target skill directory if it already exists."),
) -> None:
    """Install bundled assets, including Outcome Engineering skills."""
    try:
        skill_value = parse_skills_option(ctx.args)
        installed_paths = install_project_skills(skill_value, force=force)
    except ValueError as error:
        typer.echo(str(error))
        raise typer.Exit(code=1) from error
    except FileExistsError as error:
        typer.echo(str(error))
        raise typer.Exit(code=1) from error

    for installed_at in installed_paths:
        typer.echo(f"Installed skill at {installed_at}")


@app.command()
def validate(
    path: Path = typer.Argument(Path("product"), help="Product graph root to validate."),
) -> None:
    """Validate a product graph directory."""
    issues = validate_graph(path)
    if not issues:
        typer.echo(f"OK: {path} is a valid product graph")
        return

    typer.echo(f"Invalid product graph: {path}")
    for issue in issues:
        typer.echo(f"- {issue.path}: {issue.message}")
    raise typer.Exit(code=1)


@app.command("tree")
def tree_command(
    path: Path = typer.Argument(Path("product"), help="Product graph root to print."),
) -> None:
    """Print the product graph tree."""
    issues = validate_graph(path)
    if issues:
        typer.echo(f"Invalid product graph: {path}")
        for issue in issues:
            typer.echo(f"- {issue.path}: {issue.message}")
        raise typer.Exit(code=1)

    root = path.resolve()
    typer.echo(str(path))
    top_level = [node for node in discover_nodes(root) if node.parent is None and node.kind not in {"vision", "strategy"}]
    for index, node in enumerate(top_level):
        print_node(node, prefix="", is_last=index == len(top_level) - 1)


@app.command("create-example")
def create_example_command(
    output: Path = typer.Option(
        Path("examples/delegation-product-graph"),
        "--output",
        "-o",
        help="Directory to create.",
    ),
    force: bool = typer.Option(False, "--force", help="Replace output directory if it already exists."),
) -> None:
    """Create an example product graph."""
    try:
        create_example(output, force=force)
    except FileExistsError as error:
        typer.echo(str(error))
        raise typer.Exit(code=1) from error
    typer.echo(f"Created example product graph at {output}")


@app.command("install-skill")
def install_skill_command(
    agent: str = typer.Option("codex", "--agent", "-a", help="Agent tool target: codex, claude, or all."),
    target: Path | None = typer.Option(None, "--target", "-t", help="Exact skill install directory. Overrides --agent."),
    force: bool = typer.Option(False, "--force", help="Replace the target skill directory if it already exists."),
) -> None:
    """Install the bundled Outcome Engineering agent skills."""
    try:
        installed_paths = [install_skill(target=target, force=force)] if target is not None else install_skills_for_agent(agent, force=force)
    except (FileExistsError, ValueError) as error:
        typer.echo(str(error))
        raise typer.Exit(code=1) from error
    for installed_at in installed_paths:
        typer.echo(f"Installed skill at {installed_at}")


@app.command()
def trace(
    selector: str = typer.Argument(..., help="Node id, slug, node directory, or marker file path."),
    root: Path = typer.Option(Path("product"), "--root", "-r", help="Product graph root."),
) -> None:
    """Show where a node sits in the product graph."""
    issues = validate_graph(root)
    if issues:
        typer.echo(f"Invalid product graph: {root}")
        for issue in issues:
            typer.echo(f"- {issue.path}: {issue.message}")
        raise typer.Exit(code=1)

    node = find_node(root, selector)
    if node is None:
        typer.echo(f"Node not found or ambiguous: {selector}")
        raise typer.Exit(code=1)

    typer.echo(f"{node.kind}: {node.slug}")
    typer.echo(f"id: {node.id}")
    typer.echo(f"path: {node.path}")
    typer.echo(f"marker: {node.marker_file}")
    if node.parent is not None:
        typer.echo(f"parent: {node.parent.id}")
        typer.echo(f"relationship: {node.relationship}")
    else:
        typer.echo("parent: <root>")

    ancestors = node_ancestors(node)
    if ancestors:
        typer.echo("")
        typer.echo("Trace:")
        for ancestor in ancestors:
            typer.echo(f"- {ancestor.kind}: {ancestor.slug}")
        typer.echo(f"- {node.kind}: {node.slug}")

    if node.children:
        typer.echo("")
        typer.echo("Children:")
        for child in node.children:
            typer.echo(f"- {child.kind}: {child.slug}")


@app.command("list")
def list_command(
    kind: str | None = typer.Argument(None, help="Optional node kind to list."),
    root: Path = typer.Option(Path("product"), "--root", "-r", help="Product graph root."),
) -> None:
    """List graph nodes."""
    issues = validate_graph(root)
    if issues:
        typer.echo(f"Invalid product graph: {root}")
        for issue in issues:
            typer.echo(f"- {issue.path}: {issue.message}")
        raise typer.Exit(code=1)

    if kind is not None and kind.endswith("s"):
        kind = kind[:-1]
    if kind is not None and kind not in KIND_TO_RELATIONSHIP:
        supported = ", ".join(sorted(KIND_TO_RELATIONSHIP))
        typer.echo(f"unsupported node kind {kind!r}; expected one of: {supported}")
        raise typer.Exit(code=1)

    nodes = find_nodes_by_kind(root, kind)
    for node in nodes:
        typer.echo(f"{node.id}\t{node.path}")


@app.command()
def show(
    selector: str = typer.Argument(..., help="Node id, slug, node directory, or marker file path."),
    root: Path = typer.Option(Path("product"), "--root", "-r", help="Product graph root."),
) -> None:
    """Print a node's marker file."""
    node = load_valid_node(root, selector)
    typer.echo(marker_content(node).rstrip())


@app.command()
def context(
    selector: str = typer.Argument(..., help="Node id, slug, node directory, or marker file path."),
    root: Path = typer.Option(Path("product"), "--root", "-r", help="Product graph root."),
) -> None:
    """Print deterministic context around a node for an agent."""
    node = load_valid_node(root, selector)
    ancestors = node_ancestors(node)

    typer.echo(f"# Context: {node.id}")
    typer.echo("")
    typer.echo("## Trace")
    for ancestor in ancestors:
        typer.echo(f"- {ancestor.id} ({ancestor.marker_file})")
    typer.echo(f"- {node.id} ({node.marker_file})")

    if node.children:
        typer.echo("")
        typer.echo("## Children")
        for child in node.children:
            typer.echo(f"- {child.id} ({child.marker_file})")

    files = supporting_files(node)
    if files:
        typer.echo("")
        typer.echo("## Supporting Files")
        for path in files:
            typer.echo(f"- {path}")

    if ancestors:
        typer.echo("")
        typer.echo("## Ancestor Content")
        for ancestor in ancestors:
            typer.echo("")
            typer.echo(f"### {ancestor.id}")
            typer.echo("")
            typer.echo(marker_content(ancestor).rstrip())

    typer.echo("")
    typer.echo("## Node Content")
    typer.echo("")
    typer.echo(marker_content(node).rstrip())


@app.command("new")
def new_command(
    kind: str = typer.Argument(..., help=f"Node kind: {', '.join(sorted(KIND_TO_RELATIONSHIP))}."),
    slug: str = typer.Argument(..., help="Filesystem slug for the node."),
    root: Path = typer.Option(Path("product"), "--root", "-r", help="Product graph root."),
    under: str | None = typer.Option(None, "--under", "-u", help="Parent node id, slug, path, or marker file."),
    title: str | None = typer.Option(None, "--title", "-t", help="Human-readable title."),
) -> None:
    """Create a product graph node in the valid location."""
    root.mkdir(parents=True, exist_ok=True)
    issues = validate_graph(root)
    if issues:
        typer.echo(f"Invalid product graph: {root}")
        for issue in issues:
            typer.echo(f"- {issue.path}: {issue.message}")
        raise typer.Exit(code=1)

    try:
        node = create_node(root, kind=kind, slug=slug, title=title, under=under)
    except (ValueError, FileExistsError) as error:
        typer.echo(str(error))
        raise typer.Exit(code=1) from error

    typer.echo(f"Created {node.id}")
    typer.echo(f"path: {node.path}")
    typer.echo(f"marker: {node.marker_file}")


def load_valid_node(root: Path, selector: str):
    issues = validate_graph(root)
    if issues:
        typer.echo(f"Invalid product graph: {root}")
        for issue in issues:
            typer.echo(f"- {issue.path}: {issue.message}")
        raise typer.Exit(code=1)

    node = find_node(root, selector)
    if node is None:
        typer.echo(f"Node not found or ambiguous: {selector}")
        raise typer.Exit(code=1)
    return node


def parse_skills_option(args: list[str]) -> str:
    if not args:
        raise ValueError("nothing to install; use --skills or --skills=agents")

    value: str | None = None
    index = 0
    while index < len(args):
        arg = args[index]
        if arg == "--skills":
            value = "claude"
        elif arg.startswith("--skills="):
            value = arg.split("=", 1)[1] or "claude"
        else:
            raise ValueError(f"unknown install option: {arg}")
        index += 1

    if value is None:
        raise ValueError("nothing to install; use --skills or --skills=agents")
    return value


def print_node(node, prefix: str, is_last: bool) -> None:
    branch = "`-- " if is_last else "|-- "
    typer.echo(f"{prefix}{branch}{node.kind}: {node.slug}")
    child_prefix = prefix + ("    " if is_last else "|   ")
    for index, child in enumerate(node.children):
        print_node(child, child_prefix, index == len(node.children) - 1)


if __name__ == "__main__":
    app()
