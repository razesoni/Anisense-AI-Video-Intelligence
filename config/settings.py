from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

VIDEO_DIR = DATA_DIR / "raw_videos"
AUDIO_DIR = DATA_DIR / "audio_extracted"
SUMMARY_DIR = DATA_DIR / "summaries"
TRANSCRIPTS_DIR = DATA_DIR / "transcripts"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"
RAW_TRANSCRIPTS = TRANSCRIPTS_DIR / "raw"
CLEANED_TRANSCRIPTS = TRANSCRIPTS_DIR / "cleaned"
SEGMENTED_TRANSCRIPTS = TRANSCRIPTS_DIR / "segments"
NORMALIZED_TRANSCRIPTS = TRANSCRIPTS_DIR / "normalized"


class Settings(BaseSettings):
    
    # API Keys
    GEMINI_API_KEY : str | None = None

    # Models
    whisper_model: str = "base"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"
    
    embedding_model: str = (
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    # Audio
    audio_format: str = "mp3"
    audio_sample_rate: int = 16000
    audio_channels: int = 1

    # Environment
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
    