from __future__ import annotations

from pathlib import Path

from .ffmpeg_tools import get_audio_metadata, detect_silence, detect_volume, detect_signal_stats
from .llm import generate_summary
from .rules import build_report_payload
from .schemas import AudioReport


class AudioAnalyzer:
    def analyze_file(self, audio_path: str | Path) -> AudioReport:
        path = Path(audio_path)
        metadata = get_audio_metadata(path)
        silence_segments = detect_silence(path)
        volume = detect_volume(path)
        stats = detect_signal_stats(path)

        payload = build_report_payload(
            file_name=path.name,
            metadata=metadata,
            silence_segments=silence_segments,
            volume=volume,
            stats=stats,
        )
        payload["summary"] = generate_summary(payload)
        return AudioReport.model_validate(payload)
