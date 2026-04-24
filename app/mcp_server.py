from __future__ import annotations

from pathlib import Path
from typing import Any

from fastmcp import FastMCP

from app.analyzer import AudioAnalyzer
from app.ffmpeg_tools import (
    get_audio_metadata as ffmpeg_get_audio_metadata,
    detect_silence as ffmpeg_detect_silence,
    detect_volume as ffmpeg_detect_volume,
    detect_signal_stats as ffmpeg_detect_signal_stats,
)
from app.rules import build_report_payload


mcp = FastMCP(
    name="Audio Analysis Agent",
    instructions=(
        "Tools for analyzing audio files using FFmpeg. "
        "Use these tools to inspect metadata, detect silence, check volume, "
        "detect potential clipping, and produce structured audio quality reports."
    ),
)


def _validate_file_path(path: str) -> str:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    return str(file_path)


def _to_dict(report: Any) -> dict[str, Any]:
    if hasattr(report, "model_dump"):
        return report.model_dump()
    if hasattr(report, "dict"):
        return report.dict()
    return report


@mcp.tool
def get_audio_metadata(path: str) -> dict[str, Any]:
    print(f"[MCP] get_audio_metadata called with: {path}")
    
    """
    Extract audio metadata from an audio file using ffprobe.

    Returns duration, bitrate, sample rate, channel count, and codec name.
    """
    safe_path = _validate_file_path(path)
    return ffmpeg_get_audio_metadata(safe_path)


@mcp.tool
def detect_silence(path: str) -> list[dict[str, float]]:
    """
    Detect silence segments in an audio file using FFmpeg silencedetect.

    Returns a list of silence segments with start, end, and duration.
    """
    safe_path = _validate_file_path(path)
    return ffmpeg_detect_silence(safe_path)


@mcp.tool
def detect_volume(path: str) -> dict[str, Any]:
    """
    Analyze volume levels using FFmpeg volumedetect.

    Returns average volume and maximum volume in dB.
    """
    safe_path = _validate_file_path(path)
    return ffmpeg_detect_volume(safe_path)


@mcp.tool
def detect_signal_stats(path: str) -> dict[str, Any]:
    """
    Extract audio signal statistics using FFmpeg astats.

    Returns peak level, RMS level, noise floor, and peak count when available.
    """
    safe_path = _validate_file_path(path)
    return ffmpeg_detect_signal_stats(safe_path)


@mcp.tool
def detect_clipping(path: str) -> dict[str, Any]:
    """
    Detect possible clipping using peak-level heuristics.

    This is heuristic-based, not a guaranteed clipping classifier.
    """
    safe_path = _validate_file_path(path)

    volume = ffmpeg_detect_volume(safe_path)
    stats = ffmpeg_detect_signal_stats(safe_path)

    max_volume = volume.get("max_volume_db")
    peak_level = stats.get("peak_level_dbfs")
    peak_count = stats.get("peak_count") or 0

    potential_clipping = any([
        max_volume is not None and max_volume >= -0.1,
        peak_level is not None and peak_level >= -0.1,
        peak_count > 0 and peak_level is not None and peak_level >= -1.0,
    ])

    return {
        "potential_clipping": potential_clipping,
        "max_volume_db": max_volume,
        "peak_level_dbfs": peak_level,
        "peak_count": peak_count,
        "note": "Clipping detection is heuristic-based.",
    }


@mcp.tool
def analyze_audio_file(path: str) -> dict[str, Any]:
    """
    Run the full audio analysis pipeline for a single file.

    Returns structured metadata, audio quality metrics, issues, and suggested actions.
    """
    safe_path = _validate_file_path(path)

    analyzer = AudioAnalyzer()
    report = analyzer.analyze_file(safe_path)
    report_dict = _to_dict(report)

    if "analysis_version" not in report_dict:
        report_dict["analysis_version"] = "1.0"

    if "status" not in report_dict:
        report_dict["status"] = "success"

    return report_dict


@mcp.tool
def build_audio_report_from_tools(path: str) -> dict[str, Any]:
    """
    Build an audio report by explicitly calling the lower-level FFmpeg tool wrappers.

    This demonstrates the composable tool approach behind the pipeline.
    """
    safe_path = _validate_file_path(path)

    metadata = ffmpeg_get_audio_metadata(safe_path)
    silence_segments = ffmpeg_detect_silence(safe_path)
    volume = ffmpeg_detect_volume(safe_path)
    stats = ffmpeg_detect_signal_stats(safe_path)

    payload = build_report_payload(
        file_name=Path(safe_path).name,
        metadata=metadata,
        silence_segments=silence_segments,
        volume=volume,
        stats=stats,
    )

    payload["analysis_version"] = "1.0"
    payload["status"] = "success"

    return payload


if __name__ == "__main__":
    mcp.run()