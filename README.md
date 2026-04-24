# Audio Analysis Agent (Starter Project)

A Python starter project for analyzing court deposition audio with FFmpeg/FFprobe and optionally generating human-readable insights with an LLM.

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

### 2) Create virtual environment

```bash
python -m venv .venv
```

Activate it:

- Windows PowerShell
```powershell
.\.venv\Scripts\Activate.ps1
```
- macOS/Linux
```bash
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Optional: configure LLM

Copy environment file:

```bash
cp .env.example .env
```

Then set:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

If you skip this step, the project still runs and generates a rule-based summary.

## Run single-file analysis

```bash
python -m app.main examples/deposition_001.wav --output report.json
```

## Run batch analysis

```bash
python -m app.batch examples/ --output batch_report.json
```

## Optional MCP server

Install FastMCP separately if you want the bonus:

```bash
pip install fastmcp
python -m app.mcp_server
```

## Design notes

- Detection is deterministic and FFmpeg-based.
- The LLM is used only for explanation and action recommendations.
- `potential_clipping` is heuristic-based, not a hard truth label.

## Suggested next improvements

- Add unit tests for regex parsers
- Add aggregate summary across multiple files
- Add per-channel analysis
- Add transcript-aware analysis
- Add Dockerfile
