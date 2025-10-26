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


def generate_suggestions(
    kpi_table: List[Dict],
    anomalies: List[Dict],
    trend: Dict,
    prev_delta: Optional[List[Dict]] = None,
) -> List[str]:
    """
    Generate actionable suggestions based on the analysis.
    Returns a list of specific recommendations.
    """
    if not _client:
        # Fallback suggestions
        suggestions = []
        for row in kpi_table:
            if row.get("status") == "below":
                suggestions.append(f"Focus on improving {row['kpi']} - currently {abs(row['variance']):.0f} below target")
        for anomaly in anomalies[:3]:  # Top 3 anomalies
            suggestions.append(f"Investigate {anomaly['kpi']} - {anomaly['note']}")
        return suggestions[:5] if suggestions else ["Keep monitoring current performance trends"]

    prompt = f"""
Based on this business performance data, provide 3-5 specific, actionable recommendations:

KPI Performance:
{kpi_table}

Anomalies:
{anomalies}

Trends:
{trend}

Previous Period Comparison:
{prev_delta or "Not available"}

Instructions:
- Provide specific, actionable recommendations (not generic advice)
- Prioritize items that are below target or have anomalies
- If performance is good, suggest ways to maintain or accelerate growth
- Each recommendation should be one clear sentence
- Focus on what actions to take, not just observations
- Return as a numbered list (1., 2., 3., etc.)
"""
    try:
        resp = _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a business strategy advisor providing actionable recommendations."},
                {"role": "user", "content": prompt.strip()},
            ],
            temperature=0.3,
        )
        content = (resp.choices[0].message.content or "").strip()
        # Parse numbered list into array
        suggestions = []
        for line in content.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Remove numbering/bullets
                cleaned = line.lstrip('0123456789.-•) ').strip()
                if cleaned:
                    suggestions.append(cleaned)
        return suggestions[:5] if suggestions else ["Continue monitoring performance metrics"]
    except Exception:
        return ["Review KPIs that are below target", "Investigate anomalies", "Continue current successful strategies"]


def chat_with_ai(
    message: str,
    context: Dict,
    conversation_history: Optional[List[Dict]] = None
) -> str:
    """
    Have a conversational interaction about report data.

    Args:
        message: User's question or message
        context: Report context including kpi_table, summary, etc.
        conversation_history: Previous messages in the conversation

    Returns:
        AI's response
    """
    if not _client:
        return "I need an OpenAI API key to have conversations. Please set OPENAI_API_KEY in your .env file."

    system_prompt = f"""You are an AI business analyst assistant helping users understand their report data.

Current Report Context:
{context}

Instructions:
- Answer questions about the data clearly and concisely
- Provide insights and explanations when asked
- Suggest specific actions when appropriate
- Be conversational and helpful
- If asked about trends, explain what they mean
- If asked for advice, provide actionable recommendations
- Keep responses under 150 words unless asked for more detail
"""

    messages = [{"role": "system", "content": system_prompt}]

    # Add conversation history
    if conversation_history:
        messages.extend(conversation_history)

    # Add current message
    messages.append({"role": "user", "content": message})

    try:
        resp = _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.5,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"
