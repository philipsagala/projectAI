from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analyzer import AudioAnalyzer


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch process audio files in a folder.")
    parser.add_argument("input_dir", help="Folder containing audio files")
    parser.add_argument("--output", help="Output JSON file", default="batch_report.json")
    args = parser.parse_args()

    analyzer = AudioAnalyzer()
    input_dir = Path(args.input_dir)
    audio_exts = {".wav", ".mp3", ".m4a", ".aac", ".flac"}

    results = []
    for path in sorted(input_dir.iterdir()):
        if path.suffix.lower() in audio_exts and path.is_file():
            results.append(analyzer.analyze_file(path).model_dump(mode="json"))

    Path(args.output).write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {len(results)} reports to {args.output}")


if __name__ == "__main__":
    main()
