from typing import Dict, List, Optional
import os

try:
    from openai import OpenAI
    _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception:
    _client = None  # graceful fallback if key not set or SDK not available


def _fallback_summary(
    kpi_table: List[Dict],
    anomalies: List[Dict],
    trend: Dict,
    prev_delta: Optional[List[Dict]] = None,
) -> str:
    hits   = [r for r in kpi_table if r.get("status") == "above"]
    misses = [r for r in kpi_table if r.get("status") == "below"]
    lines: List[str] = []
    if hits:
        lines.append("✅ Met/exceeded: " + ", ".join(r["kpi"] for r in hits))
    if misses:
        lines.append("⚠️ Below target: " + ", ".join(r["kpi"] for r in misses))
    if anomalies:
        lines.append("🔍 " + "; ".join(f"{a['kpi']}: {a['note']}" for a in anomalies))
    if trend:
        lines.append("📈 " + "; ".join(f"{k}: {v}" for k, v in trend.items()))
    if prev_delta:
        deltas = "; ".join(
            f"{d['kpi']}: {d['delta_sign']} {abs(d['delta']):,.0f} vs last report"
            for d in prev_delta
        )
        lines.append("↔️ Change vs last: " + deltas)
    return "\n".join(lines) or "Summary not available."


def summarize_with_openai(
    kpi_table: List[Dict],
    anomalies: List[Dict],
    trend: Dict,
    prev_delta: Optional[List[Dict]] = None,
) -> str:
    """
    Use OpenAI to produce a short exec-suitable narrative.
    Falls back to a deterministic summary if OPENAI_API_KEY is not set.
    """
    if not _client:
        return _fallback_summary(kpi_table, anomalies, trend, prev_delta)

    prompt = f"""
You are an analytics assistant. Write a crisp summary for a business dashboard.

Data:
- KPI table (target vs actual): {kpi_table}
- Anomalies: {anomalies}
- Trend: {trend}
- Change vs previous report (optional): {prev_delta or []}

Instructions:
- Start with a one-line verdict: "On track / Mixed / Off track".
- Then 2–5 bullet points:
  - Which KPIs exceeded target and by how much.
  - Which KPIs missed and by how much; call out highest gaps first.
  - Mention anomalies (20%+ variance) and the trend.
  - If previous deltas are provided, add one bullet comparing to last report.
- Keep under 120 words.
"""
    try:
        resp = _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You produce concise, executive analytics summaries."},
                {"role": "user", "content": prompt.strip()},
            ],
            temperature=0.2,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception:
        return _fallback_summary(kpi_table, anomalies, trend, prev_delta)
