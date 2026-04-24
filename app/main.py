from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analyzer import AudioAnalyzer


def main() -> None:
    import argparse
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--output", default="report.json")
    args = parser.parse_args()

    analyzer = AudioAnalyzer()

    try:
        report = analyzer.analyze_file(args.input)

        if hasattr(report, "model_dump"):
            report = report.model_dump()
        elif hasattr(report, "dict"):
            report = report.dict()

    except Exception as exc:
        report = {
            "analysis_version": "1.0",
            "file_name": args.input,
            "status": "failed",
            "error": str(exc),
        }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Report written to {args.output}")

if __name__ == "__main__":
    main()
