# Audio Analysis Agent for AI Engineer Assessment

A Python project for analyzing court deposition audio with FFmpeg/FFprobe and optionally generating human-readable insights with an LLM.

## What it does

- Extracts metadata with `ffprobe`
- Detects silence segments with `ffmpeg` + `silencedetect`
- Detects volume statistics with `volumedetect`
- Extracts signal statistics with `astats`
- Produces a structured JSON report
- Adds a human-readable summary using either:
  - OpenAI API, if `OPENAI_API_KEY` is configured
  - A deterministic fallback summary if no API key is present

## Project structure

```text
app/
  analyzer.py
  batch.py
  ffmpeg_tools.py
  llm.py
  main.py
  mcp_server.py
  rules.py
  schemas.py
```

## Setup

### 1) Install FFmpeg
Make sure `ffmpeg` and `ffprobe` are available in your PATH.

Check:

```bash
ffmpeg -version
ffprobe -version
```

---

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## Usage

### Single file

```bash
python -m app.main files/sound01.wav --output report.json
```

---

### Batch

```bash
python -m app.batch files --output batch_report.json
```

---

## Supported Formats

* wav
* mp3
* m4a
* flac
* aac
* ogg

---

## Heuristics

### Silence

* segment threshold: ≥ 3 seconds
* high silence ratio: ≥ 20%
* severe silence ratio: ≥ 40%

### Volume

* low volume: avg < -35 dB

### Clipping

* based on peak levels near 0 dBFS

---

## Limitations

* clipping detection is heuristic-based
* noise floor is approximate
* no transcription or speaker detection
* not optimized for real-time processing

---

## Architecture

```text
Audio File
   ↓
FFmpeg / ffprobe
   ↓
Signal Analysis
   ↓
Rule-based processing
   ↓
Structured JSON output
```
