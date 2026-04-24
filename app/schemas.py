from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class SilenceSegment(BaseModel):
    start: float
    end: float
    duration: float


class Metadata(BaseModel):
    duration_seconds: float = 0.0
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    codec_name: Optional[str] = None


class AudioQuality(BaseModel):
    silence_ratio: float = 0.0
    avg_volume_db: Optional[float] = None
    max_volume_db: Optional[float] = None
    peak_level_dbfs: Optional[float] = None
    rms_level_dbfs: Optional[float] = None
    noise_floor_dbfs: Optional[float] = None
    peak_count: Optional[int] = None
    low_volume_detected: bool = False
    potential_clipping: bool = False


class AudioReport(BaseModel):
    file_name: str
    metadata: Metadata
    audio_quality: AudioQuality
    silence_segments: List[SilenceSegment] = Field(default_factory=list)
    issues: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    suggested_actions: List[str] = Field(default_factory=list)
