from __future__ import annotations

from typing import Any

def dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))

def build_report_payload(
    file_name: str,
    metadata: dict[str, Any],
    silence_segments: list[dict[str, float]],
    volume: dict[str, Any],
    stats: dict[str, Any],
) -> dict[str, Any]:
    duration = metadata.get("duration_seconds", 0.0) or 0.0
    total_silence = sum(seg.get("duration", 0.0) for seg in silence_segments)
    silence_ratio = round(total_silence / duration, 4) if duration > 0 else 0.0

    avg_volume = volume.get("avg_volume_db")
    max_volume = volume.get("max_volume_db")
    peak_level = stats.get("peak_level_dbfs")
    rms_level = stats.get("rms_level_dbfs")
    noise_floor = stats.get("noise_floor_dbfs")
    peak_count = stats.get("peak_count") or 0

    low_volume_detected = avg_volume is not None and avg_volume < -35

    potential_clipping = any([
        max_volume is not None and max_volume >= -0.1,
        peak_level is not None and peak_level >= -0.1,
        peak_count > 0 and peak_level is not None and peak_level >= -1.0,
    ])

    issues: list[str] = []
    suggested_actions: list[str] = []

    # Silence segment issues
    for seg in silence_segments:
        start = seg.get("start", 0.0)
        end = seg.get("end", 0.0)
        seg_duration = seg.get("duration", 0.0)

        if seg_duration >= 3:
            issues.append(
                f"Silence detected between {start:.1f}s and {end:.1f}s "
                f"({seg_duration:.1f}s)"
            )

        if seg_duration >= 15:
            issues.append(
                f"Long silence detected between {start:.1f}s and {end:.1f}s"
            )

    # Global silence quality
    if silence_ratio >= 0.4:
        issues.append(
            f"Severe silence ratio detected: {silence_ratio:.0%} of the audio is silent"
        )
        suggested_actions.append(
            "Audio may require significant editing due to high silence proportion"
        )
    elif silence_ratio >= 0.2:
        issues.append(
            f"High silence ratio detected: {silence_ratio:.0%} of the audio is silent"
        )
        suggested_actions.append(
            "Review and trim extended silence segments before downstream use"
        )
    elif silence_ratio > 0.10:
        suggested_actions.append(
            "Review moderate silence sections before downstream use"
        )

    # Volume quality
    if low_volume_detected:
        issues.append("Overall volume is unusually low")
        suggested_actions.append(
            "Increase microphone input gain or normalize the recording"
        )

    # Clipping quality
    if potential_clipping:
        issues.append("Possible clipping detected near peak levels")
        suggested_actions.append(
            "Reduce input gain and re-check recording levels on future captures"
        )

    # Overall fallback
    if not issues:
        suggested_actions.append(
            "Audio appears generally usable for review and transcription"
        )

    issues = dedupe(issues)
    suggested_actions = dedupe(suggested_actions)

    return {
        "analysis_version": "1.0",
        "file_name": file_name,
        "metadata": metadata,
        "audio_quality": {
            "silence_ratio": silence_ratio,
            "avg_volume_db": avg_volume,
            "max_volume_db": max_volume,
            "peak_level_dbfs": peak_level,
            "rms_level_dbfs": rms_level,
            "noise_floor_dbfs": noise_floor,
            "peak_count": peak_count,
            "low_volume_detected": low_volume_detected,
            "potential_clipping": potential_clipping,
        },
        "silence_segments": silence_segments,
        "issues": issues,
        "suggested_actions": suggested_actions,
    }