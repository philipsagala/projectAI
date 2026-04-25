# Audio Analysis Agent for AI Engineer Assessment

A Python-based system for analyzing court deposition audio using FFmpeg, with optional LLM-powered insights and MCP-based tool integration.

---

## 🎯 Overview

This project builds an AI-assisted audio analysis pipeline that:

- Extracts audio metadata
- Detects silence, volume issues, and potential clipping
- Produces structured JSON reports
- Generates human-readable insights using either:
  - OpenAI LLM
  - Rule-based fallback (no API required)

---

## ⚙️ Features

- FFmpeg-based audio analysis (deterministic)
- Structured JSON output for downstream systems
- LLM-powered interpretation layer (optional)
- MCP (FastMCP) tool exposure
- Batch processing support

---

## 📁 Project Structure

```
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

---

## 🚀 Setup

### 1. Install FFmpeg

```bash
ffmpeg -version
ffprobe -version
```

---

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3. (Optional) Configure OpenAI

Create a `.env` file:

```
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4o-mini
```

If no API key is provided, the system will fall back to rule-based insights.

---

## 📂 Output

All outputs are stored in the `output/` directory.

```
output/
├── report.json
├── agent_testSilence.txt
├── agent_testSilence.json
```

---

## 🧪 Usage

### Single File

```bash
python -m app.main files/sound01.wav --output output/report.json
```

---

### Batch

```bash
python -m app.batch files --output output/batch_report.json
```

---

### OpenAI + MCP Agent

```bash
python -m app.openai_mcp_agent files/testSilence.wav
```

---

## 🧠 LLM Insight Layer

The LLM is used for interpretation only (not detection).

It:
- Generates summaries
- Assigns risk (usable / risky / poor)
- Recommends actions
- Uses evidence from structured JSON

Guardrails:
- No hallucination
- Metrics must be explicit (e.g. silence_ratio=0.5)
- Volume only flagged if low_volume_detected=true
- Clipping is heuristic-based
- Fallback if LLM fails

---

## 🔌 MCP Integration

Available tools:

- get_audio_metadata
- detect_silence
- detect_volume
- detect_signal_stats
- detect_clipping
- analyze_audio_file

---

## 🤖 Agent Flow

```
User → OpenAI → MCP Tool → Analysis → Final Answer
```

---

## 🏗 Architecture

```
Audio → FFmpeg → Rules → JSON → LLM (optional)
```

---

## ⚖️ Heuristics

Silence:
- ≥ 3s segment
- ≥ 20% high
- ≥ 40% severe

Volume:
- avg < -35 dB

Clipping:
- peak near 0 dBFS

---
