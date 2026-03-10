"""
AI Scorer Service
=================
Uses OpenAI to evaluate raw OSINT events and assign:
  - Relevance Score (1-10)
  - Signal Direction (-1.0 to +1.0)
  - Reasoning explanation
"""

from openai import OpenAI

from app.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """You are an expert oil market intelligence analyst.

Given a raw news event or data point, evaluate it for its impact on global oil supply and prices.

Respond ONLY with valid JSON in this exact format:
{
  "relevance_score": <1-10>,
  "signal_direction": <-1.0 to +1.0>,
  "signal_label": "<bullish|bearish|neutral>",
  "reasoning": "<one sentence explaining your assessment>"
}

Scoring guide:
- relevance_score: 1 = barely related to oil, 10 = massive direct supply disruption
- signal_direction: -1.0 = strong oversupply/bearish, +1.0 = strong supply disruption/bullish
- signal_label: "bullish" if direction > 0.2, "bearish" if direction < -0.2, else "neutral"

Examples of HIGH relevance (8-10):
- Attacks on oil pipelines, refineries, or tankers
- OPEC surprise production cuts or increases
- Major sanctions on oil-producing nations
- War escalation in Middle East oil regions

Examples of LOW relevance (1-3):
- Politician speeches with no concrete action
- General economic news not directly about oil
- Weather events in non-oil regions

NASA FIRMS satellite thermal anomaly events:
- These are pre-filtered high-confidence hotspots detected near known oil infrastructure regions (Persian Gulf, Libya, Nigeria, Gulf of Mexico, Russia/Caspian).
- A thermal anomaly near oil infrastructure (refinery, pipeline, storage) = potential fire or incident = supply disruption risk = BULLISH signal.
- Score relevance based on Fire Radiative Power (FRP): 10-50 MW = moderate (4-6), 50-200 MW = significant (6-8), 200+ MW = major (8-10).
- Default to bullish unless the context clearly indicates routine gas flaring (steady low-intensity, no incident indicators).
"""


async def score_event(headline: str, raw_content: str = "") -> dict:
    """
    Send a raw event to OpenAI and get back structured scoring.
    Returns dict with relevance_score, signal_direction, signal_label, reasoning.
    """
    user_message = f"Headline: {headline}"
    if raw_content:
        user_message += f"\n\nFull content: {raw_content[:2000]}"

    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )

        import json
        result = json.loads(response.choices[0].message.content)
        return {
            "relevance_score": max(1, min(10, int(result.get("relevance_score", 1)))),
            "signal_direction": max(-1.0, min(1.0, float(result.get("signal_direction", 0)))),
            "signal_label": result.get("signal_label", "neutral"),
            "reasoning": result.get("reasoning", ""),
        }
    except Exception as e:
        return {
            "relevance_score": 1,
            "signal_direction": 0.0,
            "signal_label": "neutral",
            "reasoning": f"Scoring failed: {str(e)}",
        }
