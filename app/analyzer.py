from __future__ import annotations

from pathlib import Path
from typing import Any

from app.ffmpeg_tools import (
    get_audio_metadata,
    detect_silence,
    detect_volume,
    detect_signal_stats,
)
from app.rules import build_report_payload
from app.llm import generate_llm_insight


class AudioAnalyzer:
    def analyze_file(self, path: str) -> dict[str, Any]:
        metadata = get_audio_metadata(path)
        silence_segments = detect_silence(path)
        volume = detect_volume(path)
        stats = detect_signal_stats(path)

        payload = build_report_payload(
            file_name=Path(path).name,
            metadata=metadata,
            silence_segments=silence_segments,
            volume=volume,
            stats=stats,
        )

        payload["status"] = "success"
        payload["insight"] = generate_llm_insight(payload)

        return payload