from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from jinja2 import Template

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"
ERAS_DIR = ROOT / "examples" / "eras"

app = FastAPI(title="ESM Systems Demo")

PAGE = Template(
    """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>ESM Systems Demo</title>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 0; }
    .wrap { max-width: 980px; margin: 0 auto; padding: 24px; }
    .card { border: 1px solid #ddd; border-radius: 12px; padding: 16px; margin: 12px 0; }
    .row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 13px; white-space: pre-wrap; }
    .tag { display: inline-block; padding: 2px 10px; border-radius: 999px; border: 1px solid #ccc; font-size: 12px; }
    h1 { margin: 0 0 8px; }
    h2 { margin: 0 0 8px; font-size: 16px; }
    p { margin: 8px 0; }
    a { color: inherit; }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>ESM Systems Demo</h1>
    <p class="tag">Era: {{ era_title }}</p>
    <p>
      Edit <span class="mono">config/signals.yml</span> or the era’s <span class="mono">events.json</span>,
      then refresh this page.
    </p>

    <div class="card">
      <h2>Computed policy decision (demo)</h2>
      <div class="row">
        <div>
          <p><strong>Risk:</strong> {{ risk }}</p>
          <p><strong>Decision:</strong> {{ decision }}</p>
          <p><strong>Rationale:</strong> {{ rationale }}</p>
        </div>
        <div class="mono">{{ debug }}</div>
      </div>
    </div>

    <div class="card">
      <h2>Events</h2>
      {% for e in events %}
        <div class="card">
          <p><strong>{{ e.date }}</strong> — {{ e.label }}</p>
          <p>{{ e.summary }}</p>
          <div class="mono">{{ e.signals_pretty }}</div>
        </div>
      {% endfor %}
    </div>
  </div>
</body>
</html>
"""
)

def load_yaml(path: Path) -> Dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def load_events(era_slug: str) -> Tuple[str, List[Dict[str, Any]]]:
    era_dir = ERAS_DIR / era_slug
    meta = load_yaml(era_dir / "metadata.yml")
    events = json.loads((era_dir / "events.json").read_text(encoding="utf-8"))
    # sort by date
    events.sort(key=lambda x: x.get("date", ""))
    return meta["title"], events

def compute_risk(events: List[Dict[str, Any]], weights: Dict[str, float]) -> Tuple[float, Dict[str, Any]]:
    # Simple demo: average weighted signal across events, normalized by sum(weights)
    wsum = sum(weights.values()) or 1.0
    totals = {k: 0.0 for k in weights.keys()}
    for e in events:
        s = e.get("signals", {})
        for k in weights.keys():
            totals[k] += float(s.get(k, 0.0))
    n = max(len(events), 1)
    avgs = {k: totals[k] / n for k in totals.keys()}
    risk = sum(avgs[k] * weights[k] for k in weights.keys()) / wsum
    debug = {"avg_signals": avgs, "weights": weights}
    return risk, debug

def apply_policy(risk: float, policy: Dict[str, Any]) -> Tuple[str, str]:
    # Minimal rule engine for the three rules above.
    rules = policy["policy"]["rules"]
    for r in rules:
        expr = r["if"].strip()
        # only supports "risk >= x" and "risk < x"
        if ">=" in expr:
            _, rhs = expr.split(">=")
            if risk >= float(rhs.strip()):
                return r["decision"], r["rationale"]
        elif "<" in expr:
            _, rhs = expr.split("<")
            if risk < float(rhs.strip()):
                return r["decision"], r["rationale"]
    return "PROCEED", "Default rule."

@app.get("/", response_class=HTMLResponse)
def home(era: str = "ww2_1941_1945") -> HTMLResponse:
    signals_cfg = load_yaml(CONFIG_DIR / "signals.yml")
    policy_cfg = load_yaml(CONFIG_DIR / "policy.yml")
    weights = signals_cfg.get("signal_weights", {})

    era_title, events = load_events(era)
    risk, debug = compute_risk(events, weights)
    decision, rationale = apply_policy(risk, policy_cfg)

    for e in events:
        e["signals_pretty"] = json.dumps(e.get("signals", {}), indent=2)

    html = PAGE.render(
        era_title=era_title,
        events=events,
        risk=round(risk, 3),
        decision=decision,
        rationale=rationale,
        debug=json.dumps(debug, indent=2),
    )
    return HTMLResponse(html)
