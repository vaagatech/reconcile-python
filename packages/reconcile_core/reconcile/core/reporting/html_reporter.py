from __future__ import annotations

import html
import json
from typing import Any

from .types import TestRunReport


def _escape(value: str) -> str:
    return html.escape(value)


def _render_diff_block(diff: Any) -> str:
    if not diff:
        return ""
    payload = _escape(json.dumps(diff, indent=2))
    return f'<pre class="diff">{payload}</pre>'


def render_html_report(report: TestRunReport) -> str:
    suite_rows = []
    for suite in report["suites"]:
        step_rows = []
        for step in suite["results"]:
            status_class = "pass" if step["passed"] else "fail"
            message = (
                f'<p class="message">{_escape(step["message"])}</p>'
                if step.get("message")
                else ""
            )
            diff = _render_diff_block(step.get("diff")) if not step["passed"] else ""
            step_rows.append(
                f"""
            <li class="step {status_class}">
              <span class="badge">{"PASS" if step["passed"] else "FAIL"}</span>
              <span class="step-name">{_escape(step["step"])}</span>
              {message}
              {diff}
            </li>"""
            )

        suite_rows.append(
            f"""
        <section class="suite {"pass" if suite["passed"] else "fail"}">
          <h2>{_escape(suite["name"])}</h2>
          <p class="suite-status">{"PASSED" if suite["passed"] else "FAILED"}</p>
          <ul class="steps">{''.join(step_rows)}</ul>
        </section>"""
        )

    duration = report["summary"].get("durationMs") or 0
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>reconcile-engine Test Report</title>
  <style>
    :root {{
      color-scheme: light dark;
      --bg: #0f172a;
      --panel: #111827;
      --text: #e5e7eb;
      --muted: #94a3b8;
      --pass: #16a34a;
      --fail: #dc2626;
      --border: #334155;
    }}
    body {{
      margin: 0;
      font-family: ui-sans-serif, system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }}
    main {{ max-width: 960px; margin: 0 auto; padding: 2rem; }}
    h1 {{ margin-top: 0; }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
      gap: 1rem;
      margin: 1.5rem 0 2rem;
    }}
    .metric {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1rem;
    }}
    .metric strong {{ display: block; font-size: 1.5rem; }}
    .metric span {{ color: var(--muted); font-size: 0.875rem; }}
    .suite {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1rem 1.25rem;
      margin-bottom: 1rem;
    }}
    .suite.pass {{ border-left: 4px solid var(--pass); }}
    .suite.fail {{ border-left: 4px solid var(--fail); }}
    .suite h2 {{ margin: 0 0 0.25rem; font-size: 1.125rem; }}
    .suite-status {{ margin: 0 0 1rem; color: var(--muted); }}
    .steps {{ list-style: none; padding: 0; margin: 0; }}
    .step {{ padding: 0.75rem 0; border-top: 1px solid var(--border); }}
    .badge {{
      display: inline-block;
      min-width: 3rem;
      margin-right: 0.5rem;
      padding: 0.125rem 0.5rem;
      border-radius: 999px;
      font-size: 0.75rem;
      font-weight: 700;
      text-align: center;
    }}
    .step.pass .badge {{ background: rgba(22, 163, 74, 0.2); color: var(--pass); }}
    .step.fail .badge {{ background: rgba(220, 38, 38, 0.2); color: var(--fail); }}
    .message {{ margin: 0.5rem 0 0; color: var(--muted); }}
    .diff {{
      margin: 0.75rem 0 0;
      padding: 0.75rem;
      overflow-x: auto;
      background: #020617;
      border-radius: 8px;
      border: 1px solid var(--border);
      font-size: 0.8125rem;
    }}
    footer {{ margin-top: 2rem; color: var(--muted); font-size: 0.875rem; }}
  </style>
</head>
<body>
  <main>
    <h1>reconcile-engine Test Report</h1>
    <p>Generated at {_escape(report["generatedAt"])}</p>
    <div class="summary">
      <div class="metric"><strong>{report["summary"]["total"]}</strong><span>Total suites</span></div>
      <div class="metric"><strong>{report["summary"]["passed"]}</strong><span>Passed</span></div>
      <div class="metric"><strong>{report["summary"]["failed"]}</strong><span>Failed</span></div>
      <div class="metric"><strong>{duration}ms</strong><span>Duration</span></div>
    </div>
    {''.join(suite_rows)}
    <footer>
      Upload this file to any CI dashboard, artifact store, or reporting system.
    </footer>
  </main>
</body>
</html>"""
