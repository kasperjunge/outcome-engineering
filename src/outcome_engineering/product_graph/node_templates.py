from __future__ import annotations

from jinja2 import Environment, PackageLoader, StrictUndefined, select_autoescape


_ENV = Environment(
    loader=PackageLoader("outcome_engineering", "templates/nodes"),
    autoescape=select_autoescape(default=False),
    keep_trailing_newline=True,
    undefined=StrictUndefined,
)


def render_template(kind: str, slug: str, title: str) -> str:
    template = _ENV.get_template(f"{kind}.md.j2")
    return template.render(kind=kind, slug=slug, title=title)
