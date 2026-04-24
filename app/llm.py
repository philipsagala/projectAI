from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv


def generate_summary(report: dict[str, Any]) -> str:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        return fallback_summary(report)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        prompt = f"""
You are reviewing court deposition audio quality.

Given this JSON report:
{json.dumps(report, indent=2)}

Write a concise professional summary in 2-4 sentences.
Rules:
- Only mention issues present in the JSON.
- If clipping is heuristic-based, say 'possible clipping'.
- Mention whether the file seems usable for transcription/review.
- Mention one or two recommended actions.
""".strip()

        response = client.responses.create(
            model=model,
            input=prompt,
        )
        return (response.output_text or "").strip() or fallback_summary(report)
    except Exception:
        return fallback_summary(report)


def fallback_summary(report: dict[str, Any]) -> str:
    quality = report.get("audio_quality", {})
    issues = report.get("issues", [])
    actions = report.get("suggested_actions", [])

    if not issues:
        return "Audio appears generally usable with no major quality issues detected. It should be suitable for review or transcription."

    parts = ["Audio is usable but has some quality concerns."]
    if quality.get("silence_ratio", 0) > 0.10:
        parts.append("There are extended silence segments that should be reviewed or trimmed.")
    if quality.get("low_volume_detected"):
        parts.append("The overall volume is lower than expected.")
    if quality.get("potential_clipping"):
        parts.append("There are signs of possible clipping near peak levels.")
    if actions:
        parts.append("Recommended actions: " + "; ".join(actions[:2]) + ".")
    return " ".join(parts)
