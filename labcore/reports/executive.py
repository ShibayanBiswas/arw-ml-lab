"""Executive summary HTML/PDF from FACTS (ARCHITECTURE §25 / §46.4)."""

from __future__ import annotations

import base64
import html
import json
from typing import Any

from labcore.reports.builder import build_run_report

_GOLD = "#c9a227"
_INK = "#1a1a1a"


def build_executive_html(
    *,
    title: str,
    stage: str,
    facts: dict[str, Any],
    insights: dict[str, Any] | None = None,
    seed: int = 42,
) -> str:
    """Render a static HTML executive summary; numbers come only from FACTS."""
    report = build_run_report(
        title=title,
        stage=stage,
        facts=facts,
        insights=insights,
        seed=seed,
    )
    rows = "".join(
        f"<tr><th>{html.escape(str(k))}</th><td><code>{html.escape(json.dumps(v, sort_keys=True))}</code></td></tr>"
        for k, v in sorted(facts.items(), key=lambda kv: str(kv[0]))
    )
    insight_block = ""
    if insights is not None:
        insight_block = (
            "<section><h2>AI Insights (advisory)</h2>"
            f"<pre>{html.escape(json.dumps(insights, sort_keys=True, indent=2))}</pre></section>"
        )
    sections = "".join(
        f"<li><strong>{html.escape(s['title'])}</strong> "
        f"<span class='muted'>({html.escape(s['id'])})</span></li>"
        for s in report["sections"]
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>{html.escape(title)} — Executive summary</title>
<style>
body {{ font-family: system-ui, sans-serif; color: {_INK}; max-width: 52rem; margin: 2rem auto; line-height: 1.5; }}
h1 {{ font-family: Georgia, serif; border-bottom: 2px solid {_GOLD}; padding-bottom: 0.25rem; }}
h2 {{ color: {_GOLD}; font-size: 1.1rem; margin-top: 1.5rem; }}
.muted {{ color: #666; font-size: 0.85rem; }}
table {{ border-collapse: collapse; width: 100%; margin-top: 0.5rem; }}
th, td {{ border: 1px solid #ddd; padding: 0.35rem 0.5rem; text-align: left; vertical-align: top; }}
th {{ background: #faf6ea; width: 30%; }}
footer {{ margin-top: 2rem; font-size: 0.8rem; color: #666; }}
pre {{ background: #f6f6f6; padding: 0.75rem; overflow-x: auto; font-size: 0.8rem; }}
</style>
</head>
<body>
<header>
<p class="muted">REP.T.EXECUTIVE · {html.escape(stage)} · seed {seed} · {html.escape(report['timezone'])}</p>
<h1>{html.escape(title)}</h1>
<p>{html.escape(report['disclaimer'])}</p>
</header>
<section>
<h2>Outline</h2>
<ul>{sections}</ul>
</section>
<section>
<h2>FACTS</h2>
<table>{rows if rows else "<tr><td colspan='2'>No FACTS supplied.</td></tr>"}</table>
</section>
{insight_block}
<footer>Generated at {html.escape(report['created_at'])} — HTML export; PDF via WeasyPrint when available.</footer>
</body>
</html>"""


def render_executive_pdf(html_doc: str) -> bytes:
    """PDF bytes via WeasyPrint (requires Pango in the runtime image)."""
    from weasyprint import HTML

    return HTML(string=html_doc).write_pdf()


def render_executive_pdf_b64(html_doc: str) -> str:
    return base64.standard_b64encode(render_executive_pdf(html_doc)).decode("ascii")