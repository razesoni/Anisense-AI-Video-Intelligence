"""MetadataDB module for looking up full video asset metadata for search results."""

import json
import re
from pathlib import Path
from typing import Any, Dict, Optional
from config.settings import CLEANED_TRANSCRIPTS, RAW_VIDEO_DIR, SUMMARY_DIR

DEMO_VIDEOS_MAP: Dict[str, Dict[str, Any]] = {
    "Classroom-of-the-Elite_S1_Ep-06": {
        "id": "Classroom-of-the-Elite_S1_Ep-06",
        "video_title": "Classroom of the Elite",
        "season": "Season 1",
        "episode": "Episode 06",
        "duration": "24:13",
        "status": "AI Ready",
        "segments": 182,
        "summary": True,
        "thumbnail": "cote",
        "filename": "Classroom-of-the-Elite_S1_Ep-06.mp4",
        "media_url": "/media/Classroom-of-the-Elite_S1_Ep-06.mp4",
    },
    "Demon-Slayer_S1_Ep-05": {
        "id": "Demon-Slayer_S1_Ep-05",
        "video_title": "Demon Slayer",
        "season": "Season 1",
        "episode": "Episode 05",
        "duration": "23:41",
        "status": "AI Ready",
        "segments": 164,
        "summary": True,
        "thumbnail": "demon",
        "filename": "Demon-Slayer_S1_Ep-05.mp4",
        "media_url": "/media/Demon-Slayer_S1_Ep-05.mp4",
    },
}


class MetadataDB:
    """Database wrapper responsible for fetching video metadata to enrich search hits."""

    def __init__(self, raw_video_dir: Optional[Path] = None):
        self.raw_video_dir = Path(raw_video_dir or RAW_VIDEO_DIR)

    def _find_video_file(self, video_id: str) -> Optional[Path]:
        if not self.raw_video_dir.exists():
            return None
        exact = next(self.raw_video_dir.glob(f"{video_id}.*"), None)
        if exact:
            return exact

        requested_title = re.sub(r"[^a-z0-9]", "", video_id.split("_S", 1)[0].lower())
        requested_title = requested_title.replace("the", "")
        matches = []
        for video_file in self.raw_video_dir.iterdir():
            if video_file.suffix.lower() not in {".mp4", ".mpeg", ".mpv", ".mkv", ".mov", ".webm", ".avi"}:
                continue
            file_title = re.sub(r"[^a-z0-9]", "", video_file.stem.split("_S", 1)[0].lower()).replace("the", "")
            if file_title == requested_title:
                matches.append(video_file)
        return matches[0] if len(matches) == 1 else None

    def get_video_metadata(self, video_id: str) -> Dict[str, Any]:
        """Resolves video title, media URL, file paths, season, and episode details.

        Args:
            video_id: Canonical stem identifier of the video.

        Returns:
            Dictionary containing complete video metadata attributes.
        """
        if not video_id:
            video_id = "unknown"

        # Keep legacy metadata only when the corresponding media file exists.
        if video_id in DEMO_VIDEOS_MAP:
            meta = DEMO_VIDEOS_MAP[video_id].copy()
            video_file = self._find_video_file(video_id)
            if video_file:
                meta["id"] = video_file.stem
                meta["filename"] = video_file.name
                meta["media_url"] = f"/media/{video_file.name}"
                meta["video_path"] = str(video_file)
                return meta

        # 2. Search on disk for corresponding raw video file
        video_file = self._find_video_file(video_id)
        
        # 3. Parse canonical string <Sanitized-Title>_S<Season>_Ep-<Episode>
        parts = video_id.split("_")
        title_part = parts[0].replace("-", " ") if len(parts) > 0 else video_id
        season_str = "Season 1"
        episode_str = "Episode"

        for part in parts:
            if part.startswith("S") and part[1:].isdigit():
                season_str = f"Season {int(part[1:])}"
            elif "Ep-" in part:
                ep_num = part.split("Ep-")[-1]
                episode_str = f"Episode {ep_num}"

        filename = video_file.name if video_file else f"{video_id}.mp4"
        media_url = f"/media/{filename}" if video_file else f"/media/{video_id}.mp4"

        # Check transcript segment count if file exists
        cleaned_path = CLEANED_TRANSCRIPTS / f"{video_id}.json"
        segment_count = 0
        if cleaned_path.exists():
            try:
                with open(cleaned_path, "r", encoding="utf-8") as f:
                    segment_count = len(json.load(f))
            except Exception:
                segment_count = 0

        summary_exists = (SUMMARY_DIR / f"{video_id}.json").exists()

        return {
            "id": video_file.stem if video_file else video_id,
            "video_title": title_part,
            "season": season_str,
            "episode": episode_str,
            "duration": "--:--",
            "status": "AI Ready" if summary_exists else "Indexed",
            "segments": segment_count,
            "summary": summary_exists,
            "thumbnail": "cote",
            "filename": filename,
            "media_url": media_url,
            "video_path": str(video_file) if video_file else "",
        }
