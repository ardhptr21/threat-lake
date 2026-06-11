from __future__ import annotations

from pathlib import Path


def render_sql_templates(base_dir: str | Path, catalog: str, namespace: str) -> list[str]:
    base = Path(base_dir)
    rendered: list[str] = []
    for group in ("bronze", "silver", "gold"):
        for path in sorted((base / group).glob("*.sql")):
            text = path.read_text(encoding="utf-8")
            rendered.append(text.replace("${CATALOG}", catalog).replace("${NAMESPACE}", namespace))
    return rendered

