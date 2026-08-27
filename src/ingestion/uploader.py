import re
import uuid
from pathlib import Path
from typing import BinaryIO
from config.settings import settings
from src.ingestion.validator import VideoMetadata, VideoValidator


def format_canonical_filename(
    title: str, season: int, episode: int, original_filename: str
) -> str:
    """Formats the filename into: <Sanitized-Title>_S<Season>_Ep-<Episode>.<ext>

    Example: Classroom-of-the-Elite_S1_Ep-06.mp4
    """
    # Replace spaces and underscores with hyphens
    sanitized_title = re.sub(r'[\s_]+', '-', title.strip())
    # Strip any characters that are not alphanumeric or hyphens
    sanitized_title = re.sub(r'[^a-zA-Z0-9\-]', '', sanitized_title)

    ext = Path(original_filename).suffix.lower()
    return f"{sanitized_title}_S{int(season)}_Ep-{int(episode):02d}{ext}"


class VideoUploader:

  def __init__(self, target_dir: Path | None = None):
    self.target_dir = Path(target_dir or settings.RAW_VIDEO_DIR).expanduser().resolve()
    self.target_dir.mkdir(parents=True, exist_ok=True)
    self.validator = VideoValidator(
        allowed_extensions=settings.ALLOWED_EXTENSIONS,
        max_size_mb=settings.MAX_FILE_SIZE_MB,
        allowed_codecs=settings.ALLOWED_CODECS,
    )

  def save_and_validate(
      self, file_stream: BinaryIO, canonical_filename: str
  ) -> tuple[str, Path, VideoMetadata]:
    # 1. Validate the extension of the canonical filename
    self.validator.validate_extension(canonical_filename)

    # 2. Assign an internal UUID for database tracking
    video_id = str(uuid.uuid4())

    # 3. Save directly using the canonical filename on disk
    dest_path = self.target_dir / canonical_filename

    try:
      # Write chunks to disk
      with open(dest_path, 'wb') as buffer:
        while chunk := file_stream.read(settings.CHUNK_SIZE_BYTES):
          buffer.write(chunk)

      # Validate size and codec integrity
      self.validator.validate_size(dest_path)
      metadata = self.validator.probe_integrity_and_codecs(dest_path)

      return video_id, dest_path, metadata

    except Exception:
      if dest_path.exists():
        dest_path.unlink()  # Clean up failed/corrupted file
      raise