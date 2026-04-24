from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.analyzer import AudioAnalyzer


SUPPORTED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac", ".aac", ".ogg"}


def aggregate_summary(reports: list[dict]) -> dict:
    total_files = len(reports)

    if total_files == 0:
        return {
            "total_files": 0,
            "files_with_issues": 0,
            "avg_silence_ratio": 0.0,
            "potential_clipping_files": 0,
            "low_volume_files": 0,
        }

    files_with_issues = sum(1 for r in reports if r.get("issues"))
    avg_silence_ratio = sum(
        r.get("audio_quality", {}).get("silence_ratio", 0.0)
        for r in reports
    ) / total_files

    potential_clipping_files = sum(
        1 for r in reports
        if r.get("audio_quality", {}).get("potential_clipping") is True
    )

    low_volume_files = sum(
        1 for r in reports
        if r.get("audio_quality", {}).get("low_volume_detected") is True
    )

    return {
        "total_files": total_files,
        "files_with_issues": files_with_issues,
        "avg_silence_ratio": round(avg_silence_ratio, 4),
        "potential_clipping_files": potential_clipping_files,
        "low_volume_files": low_volume_files,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir")
    parser.add_argument("--output", default="batch_report.json")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    analyzer = AudioAnalyzer()

    reports = []

    for file_path in input_dir.iterdir():
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        report = analyzer.analyze_file(str(file_path))

        if hasattr(report, "model_dump"):
            report = report.model_dump()
        elif hasattr(report, "dict"):
            report = report.dict()

        reports.append(report)

    payload = {
        "analysis_version": "1.0",
        "summary": aggregate_summary(reports),
        "reports": reports,
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"Batch report written to {args.output}")


if __name__ == "__main__":
    main()