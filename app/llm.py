from __future__ import annotations

import json
import os
from typing import Any, Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError


load_dotenv()


RiskLevel = Literal["usable", "risky", "poor"]


class LLMInsight(BaseModel):
    llm_provider: str = Field(default="openai")
    risk_assessment: RiskLevel
    summary: str
    evidence: list[str]
    recommended_actions: list[str]


def build_rule_based_insight(report: dict[str, Any]) -> dict[str, Any]:
    issues = report.get("issues", [])
    actions = report.get("suggested_actions", [])
    audio_quality = report.get("audio_quality", {})

    silence_ratio = audio_quality.get("silence_ratio", 0.0) or 0.0
    low_volume = audio_quality.get("low_volume_detected", False)
    clipping = audio_quality.get("potential_clipping", False)

    evidence: list[str] = []

    if silence_ratio >= 0.4:
        risk: RiskLevel = "risky"
        summary = (
            "Audio is usable but has significant silence-related quality concerns "
            "that should be reviewed before downstream use."
        )
        evidence.append(
            f"silence_ratio={silence_ratio} exceeds severe threshold of 0.4"
        )

    elif clipping:
        risk = "risky"
        summary = (
            "Audio may be usable, but possible clipping was detected and should be reviewed."
        )
        evidence.append("potential_clipping=true")

    elif low_volume:
        risk = "risky"
        summary = (
            "Audio may be difficult to review or transcribe because the overall volume is low."
        )
        evidence.append("low_volume_detected=true")

    elif issues:
        risk = "usable"
        summary = "Audio is mostly usable, but some quality issues were detected."
        evidence.extend(issues)

    else:
        risk = "usable"
        summary = (
            "Audio appears generally usable with no major quality issues detected."
        )
        evidence.append("No issues were detected in the structured audio report.")

    evidence.extend(issues)

    return LLMInsight(
        llm_provider="rule_based_fallback",
        risk_assessment=risk,
        summary=summary,
        evidence=list(dict.fromkeys(evidence)),
        recommended_actions=actions
        or ["Audio appears generally usable for review and transcription"],
    ).model_dump()


def build_llm_prompt(report: dict[str, Any]) -> str:
    return f"""
You are reviewing an audio quality report for a court deposition recording.

You must interpret the structured JSON report only.
Do not infer or invent issues that are not present in the JSON.

Your tasks:
1. Write a concise context-aware summary.
2. Classify risk as exactly one of: usable, risky, poor.
3. Recommend practical actions based only on detected issues.
4. Provide evidence using exact fields or issue messages from the JSON.
5. Tie severity to measurable thresholds when relevant.

Risk guidance:
- usable: no issues or only minor issues
- risky: significant silence, low volume, or possible clipping that may affect review/transcription
- poor: multiple severe issues or audio quality likely prevents reliable review/transcription

Important guardrails:
- Do not say clipping exists unless potential_clipping is true.
- If clipping is present, call it "possible clipping" because it is heuristic-based.
- Do not mention transcription issues unless supported by issues, silence ratio, low volume, or clipping.
- Do not interpret volume as a quality issue unless low_volume_detected is true.
- If low_volume_detected is false, treat avg_volume_db as normal and do not describe it as low or suboptimal.
- Do not mention normal metrics unless they are directly needed to explain the risk.
- When referencing metrics, include exact values (e.g., silence_ratio=0.5).
- If there are no issues, say the audio is generally usable.
- Return only valid JSON.
- Do not wrap the JSON in markdown.

Return this exact JSON shape:
{{
  "llm_provider": "openai",
  "risk_assessment": "usable | risky | poor",
  "summary": "...",
  "evidence": ["..."],
  "recommended_actions": ["..."]
}}

Structured audio report:
{json.dumps(report, indent=2)}
""".strip()


def generate_llm_insight(report: dict[str, Any]) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        return build_rule_based_insight(report)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        response = client.responses.create(
            model=model,
            input=build_llm_prompt(report),
            temperature=0.2,
        )

        raw_text = response.output_text.strip()
        parsed = json.loads(raw_text)

        validated = LLMInsight(**parsed)
        return validated.model_dump()

    except (json.JSONDecodeError, ValidationError, Exception) as exc:
        fallback = build_rule_based_insight(report)
        fallback["llm_error"] = str(exc)
        return fallback