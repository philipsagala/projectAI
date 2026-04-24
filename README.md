# Audio Analysis Agent (FFmpeg + LLM)

## Overview

This project is a simple audio analysis pipeline designed to process court deposition recordings and generate structured insights about audio quality.

The system focuses on:

* extracting audio metadata
* detecting silence and volume issues
* producing structured JSON output
* handling batch processing reliably

---

## Features

### Audio Analysis (FFmpeg)

* Extract:

  * duration
  * bitrate
  * sample rate
  * channels

* Detect:

  * silence segments
  * silence ratio
  * low volume
  * potential clipping

---

### Structured Output

Example:

```json
{
  "analysis_version": "1.0",
  "status": "success",
  "file_name": "example.wav",
  "metadata": {
    "duration_seconds": 10.0,
    "bitrate": 705662,
    "sample_rate": 44100,
    "channels": 1,
    "codec_name": "pcm_s16le"
  },
  "audio_quality": {
    "silence_ratio": 0.5,
    "avg_volume_db": -24.1,
    "max_volume_db": -18.1,
    "low_volume_detected": false,
    "potential_clipping": false
  },
  "issues": [
    "Silence detected between 5.0s and 10.0s (5.0s)",
    "Severe silence ratio detected: 50% of the audio is silent"
  ],
  "suggested_actions": [
    "Audio may require significant editing due to high silence proportion"
  ]
}
```

---

### Batch Processing

Process multiple files in a directory:

```bash
python -m app.batch files --output batch_report.json
```

Example output:

```json
{
  "analysis_version": "1.0",
  "summary": {
    "total_files": 3,
    "successful_files": 3,
    "failed_files": 0,
    "files_with_issues": 1,
    "avg_silence_ratio": 0.1667
  },
  "reports": [...]
}
```

---

### Error Handling

The system returns structured errors instead of crashing.

Example:

```json
{
  "analysis_version": "1.0",
  "status": "failed",
  "file_name": "corrupt.wav",
  "error": "Invalid data found when processing input"
}
```

---

## Installation

### Install FFmpeg

Mac (Homebrew):

```bash
brew install ffmpeg
```

Verify:

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
