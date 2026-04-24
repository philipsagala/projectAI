from __future__ import annotations

from .ffmpeg_tools import get_audio_metadata, detect_silence, detect_volume, detect_signal_stats

try:
    from fastmcp import FastMCP
except Exception:  # pragma: no cover
    FastMCP = None


if FastMCP is not None:
    mcp = FastMCP("audio-analysis-tools")

    @mcp.tool
    def get_audio_metadata_tool(path: str) -> dict:
        return get_audio_metadata(path)

    @mcp.tool
    def detect_silence_tool(path: str, noise_db: int = -40, min_duration: int = 2) -> list[dict]:
        return detect_silence(path, noise_db=noise_db, min_duration=min_duration)

    @mcp.tool
    def detect_volume_tool(path: str) -> dict:
        return detect_volume(path)

    @mcp.tool
    def detect_signal_stats_tool(path: str) -> dict:
        return detect_signal_stats(path)


if __name__ == "__main__" and FastMCP is not None:
    mcp.run()
