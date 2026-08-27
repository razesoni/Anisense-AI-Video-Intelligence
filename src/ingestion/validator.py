import json
import shutil
import subprocess
from pathlib import Path
from typing import NamedTuple

from config.settings import settings


class VideoMetadata(NamedTuple):
    duration_seconds: float
    video_codec: str | None
    audio_codec: str | None
    file_size_bytes: int

class VideoValidator:
    def __init__(self, allowed_extensions: set[str], max_size_mb: int, allowed_codecs: set[str] | None = None  ):
        self.allowed_extensions = allowed_extensions
        self.max_size_bytes = max_size_mb * 1024 * 1024 
        self.allowed_codecs = allowed_codecs or set()

    def validate_extension(self, filename: str) -> str:
        ext = Path(filename).suffix.lower()
        if ext not in self.allowed_extensions:
            raise ValueError(f"Unsupported extension: {ext}. Allowed: {self.allowed_extensions}")
        return ext

    def validate_size(self, file_path: Path) -> int:
        file_size = file_path.stat().st_size
        if file_size == 0:
            raise ValueError("File is empty")
        if file_size > self.max_size_bytes:
            raise ValueError(f"File size exceeds limit: {file_size / (1024*1024):.2f} MB. Max allowed: {self.max_size_bytes / (1024*1024):.2f} MB")
        return file_size
    
    def probe_integrity_and_codecs(self, file_path: Path) -> VideoMetadata:
        if not shutil.which("ffprobe"):
            raise RuntimeError("ffprobe is required but not installed.")

        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration, size:stream=codec_type,codec_name",
            "-of", "json",
            str(file_path)
        ]
        result = subprocess.run(
            cmd, 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            raise ValueError(f"File is corrupted or invalid. ffprobe error: {result.stderr}")

        probe_data = json.loads(result.stdout)
        streams = probe_data.get("streams", [])
        format_info = probe_data.get("format", {})

        video_codec = next((s["codec_name"] for s in streams if s["codec_type"] == "video"), None)
        audio_codec = next((s["codec_name"] for s in streams if s["codec_type"] == "audio"), None)

        if not audio_codec:
            raise ValueError("File must contain audio track.")
        
        duration = float(format_info.get("duration", 0.0))
        if duration <= 0: 
            raise ValueError("Video duration is zero or invalid")

        return VideoMetadata(
            duration_seconds=duration,
            video_codec=video_codec,
            audio_codec=audio_codec,
            file_size_bytes=int(format_info.get("size", file_path.stat().st_size))
        )
        