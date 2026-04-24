from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analyzer import AudioAnalyzer


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze an audio file and produce a JSON report.")
    parser.add_argument("input", help="Path to audio file")
    parser.add_argument("--output", help="Path to write JSON report", default=None)
    args = parser.parse_args()

    analyzer = AudioAnalyzer()
    report = analyzer.analyze_file(args.input)
    report_json = report.model_dump(mode="json")

    if args.output:
        Path(args.output).write_text(json.dumps(report_json, indent=2), encoding="utf-8")
    else:
        print(json.dumps(report_json, indent=2))


if __name__ == "__main__":
    main()
