from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


class FFmpegToolError(RuntimeError):
    pass


def _run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, check=check)
    except FileNotFoundError as exc:
        raise FFmpegToolError("ffmpeg/ffprobe not found. Install FFmpeg and ensure it is in PATH.") from exc
    except subprocess.CalledProcessError as exc:
        raise FFmpegToolError(exc.stderr.strip() or "Command failed") from exc


def get_audio_metadata(audio_path: str | Path) -> dict[str, Any]:
    audio_path = str(audio_path)
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration,bit_rate:stream=sample_rate,channels,codec_name",
        "-of", "json",
        audio_path,
    ]
    result = _run(cmd)
    raw = json.loads(result.stdout)
    fmt = raw.get("format", {})
    streams = raw.get("streams", [])
    stream = streams[0] if streams else {}

    return {
        "duration_seconds": float(fmt.get("duration", 0) or 0),
        "bitrate": int(fmt["bit_rate"]) if fmt.get("bit_rate") else None,
        "sample_rate": int(stream["sample_rate"]) if stream.get("sample_rate") else None,
        "channels": int(stream["channels"]) if stream.get("channels") else None,
        "codec_name": stream.get("codec_name"),
    }


def detect_silence(audio_path: str | Path, noise_db: int = -40, min_duration: int = 2) -> list[dict[str, float]]:
    audio_path = str(audio_path)
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-i", audio_path,
        "-af", f"silencedetect=noise={noise_db}dB:d={min_duration}",
        "-f", "null",
        "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    log = result.stderr

    starts = [float(x) for x in re.findall(r"silence_start:\s*([\d\.]+)", log)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*([\d\.]+)", log)]
    durs = [float(x) for x in re.findall(r"silence_duration:\s*([\d\.]+)", log)]

    segments: list[dict[str, float]] = []
    for start, end, dur in zip(starts, ends, durs):
        segments.append({"start": start, "end": end, "duration": dur})
    return segments


def detect_volume(audio_path: str | Path) -> dict[str, float | None]:
    audio_path = str(audio_path)
    cmd = ["ffmpeg", "-hide_banner", "-i", audio_path, "-af", "volumedetect", "-f", "null", "-"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    log = result.stderr

    mean_match = re.search(r"mean_volume:\s*([-\d\.]+) dB", log)
    max_match = re.search(r"max_volume:\s*([-\d\.]+) dB", log)

    return {
        "avg_volume_db": float(mean_match.group(1)) if mean_match else None,
        "max_volume_db": float(max_match.group(1)) if max_match else None,
    }


def detect_signal_stats(audio_path: str | Path) -> dict[str, float | int | None]:
    audio_path = str(audio_path)
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-i", audio_path,
        "-af", "astats=metadata=1:reset=0",
        "-f", "null",
        "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    log = result.stderr

    def extract_float(pattern: str):
        match = re.search(pattern, log)
        if not match:
            return None

        value = match.group(1).strip()

        if value in ("-", "-inf", "inf", "nan"):
            return None
        try:
            return float(value)
        except ValueError:
            return None

    def extract_int(pattern: str) -> int | None:
        match = re.search(pattern, log)
        return int(match.group(1)) if match else None

    return {
        "peak_level_dbfs": extract_float(r"Peak level dB:\s*([-\d\.]+)"),
        "rms_level_dbfs": extract_float(r"RMS level dB:\s*([-\d\.]+)"),
        "noise_floor_dbfs": extract_float(r"Noise floor dB:\s*([-\d\.]+)"),
        "peak_count": extract_int(r"Peak count:\s*(\d+)"),
    }
