import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from api.routes.ingestion_routes import router as ingestion_router
from api.routes.summary_routes import router as summary_router
from api.routes.search_routes import router as search_router
from config.settings import CLEANED_TRANSCRIPTS, RAW_VIDEO_DIR, SUMMARY_DIR
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="AniSense AI API & UI")

# Enable CORS for cross-origin frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base directory paths
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "frontend" / "static"
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"

# Mount static files and Jinja2 templates
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/media", StaticFiles(directory=str(RAW_VIDEO_DIR)), name="media")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Register API Routers
app.include_router(ingestion_router)
app.include_router(summary_router)
app.include_router(search_router)

def format_duration(duration_seconds: float | int | None) -> str:
  if duration_seconds is None or duration_seconds < 0:
    return "--:--"
  total_seconds = int(round(duration_seconds))
  hours, remainder = divmod(total_seconds, 3600)
  minutes, seconds = divmod(remainder, 60)
  return f"{hours}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes:02d}:{seconds:02d}"


def format_timestamp(seconds: float | int | None) -> str:
  total_seconds = max(0, int(round(seconds or 0)))
  hours, remainder = divmod(total_seconds, 3600)
  minutes, seconds = divmod(remainder, 60)
  return f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes:02d}:{seconds:02d}"


def get_video_duration(video_file: Path) -> float | None:
  if not shutil.which("ffprobe"):
    return None
  try:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(video_file)],
        capture_output=True,
        text=True,
        check=True,
    )
    duration = float(result.stdout.strip())
    return duration if duration > 0 else None
  except (OSError, ValueError, subprocess.CalledProcessError):
    return None


def get_videos() -> list[dict[str, Any]]:
  """Build the library from ingested files and generated artifacts."""
  videos = {}
  RAW_VIDEO_DIR.mkdir(parents=True, exist_ok=True)

  for video_file in RAW_VIDEO_DIR.iterdir():
    if not video_file.is_file() or video_file.suffix.lower() not in {
        ".mp4", ".mpeg", ".mpv", ".mkv", ".mov", ".webm", ".avi"
    }:
      continue

    video_id = video_file.stem
    title_part, _, episode_part = video_id.rpartition("_S")
    episode_number = episode_part.split("_Ep-", 1)[-1] if "_Ep-" in episode_part else ""
    cleaned_path = CLEANED_TRANSCRIPTS / f"{video_id}.json"
    summary_exists = (SUMMARY_DIR / f"{video_id}.json").exists()
    segment_count = 0
    if cleaned_path.exists():
      try:
        with open(cleaned_path, "r", encoding="utf-8") as f:
          segment_count = len(json.load(f))
      except (OSError, json.JSONDecodeError):
        segment_count = 0

    duration_seconds = get_video_duration(video_file)
    videos[video_id] = {
        "id": video_id,
        "title": title_part.replace("-", " ") if title_part else video_id,
        "episode": f"Episode {episode_number}" if episode_number else "Episode",
        "duration_seconds": duration_seconds,
        "duration": format_duration(duration_seconds),
        "status": "AI Ready" if summary_exists else "Processing",
        "segments": segment_count,
        "summary": summary_exists,
        "thumbnail": "cote",
        "filename": video_file.name,
    }

  return sorted(videos.values(), key=lambda video: video["id"])


def get_dashboard_data() -> dict[str, Any]:
  videos = get_videos()
  duration_seconds = sum(video.get("duration_seconds") or 0 for video in videos)
  return {
      "stats": {
        "videos_processed": len(videos),
        "total_duration_seconds": duration_seconds,
        "total_duration": format_duration(duration_seconds),
        "ai_summaries": sum(1 for video in videos if video.get("summary")),
        "indexed_segments": sum(video.get("segments") or 0 for video in videos),
      },
      "videos": videos,
  }


def load_video_summary(video_stem: str) -> dict[str, Any] | None:
  """Loads the generated summary JSON produced by the ingestion pipeline."""
  summary_file = Path(SUMMARY_DIR) / f"{video_stem}.json"
  if summary_file.exists():
    try:
      with open(summary_file, "r", encoding="utf-8") as f:
        return json.load(f)
    except Exception:
      return None
  return None


def load_video_transcript(video_stem: str) -> list[dict[str, Any]]:
  transcript_file = CLEANED_TRANSCRIPTS / f"{video_stem}.json"
  if not transcript_file.exists():
    return []
  try:
    with open(transcript_file, "r", encoding="utf-8") as f:
      transcript = json.load(f)
    return transcript if isinstance(transcript, list) else []
  except (OSError, json.JSONDecodeError):
    return []


# --- HTML Frontend Routes (Jinja2) ---


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
  return templates.TemplateResponse(request=request, name="index.html")


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
  dashboard_data = get_dashboard_data()
  return templates.TemplateResponse(
  request=request, name="dashboard.html", context=dashboard_data
  )


@app.get("/upload", response_class=HTMLResponse)
async def upload(request: Request):
  return templates.TemplateResponse(request=request, name="upload.html")


@app.get("/library", response_class=HTMLResponse)
async def library(request: Request):
  return templates.TemplateResponse(
  request=request, name="library.html", context={"videos": get_videos()}
  )


@app.get("/search", response_class=HTMLResponse)
async def search(request: Request):
  return templates.TemplateResponse(
  request=request, name="search.html", context={"videos": get_videos()}
  )


@app.get("/summaries", response_class=HTMLResponse, name="summaries")
async def summaries(request: Request):
  return templates.TemplateResponse(
      request=request, name="summaries.html", context={"videos": get_videos()}
  )


@app.get("/analytics", response_class=HTMLResponse, name="analytics")
async def analytics(request: Request):
  return templates.TemplateResponse(request=request, name="analytics.html")


@app.get("/video/{video_id}", response_class=HTMLResponse, name="video")
async def video_view(request: Request, video_id: str):
  video = next(
      (v for v in get_videos() if str(v["id"]) == str(video_id)),
      {
          "id": video_id,
          "title": video_id.replace("-", " "),
          "episode": "Episode",
          "duration": "--:--",
          "status": "AI Ready",
      },
  )
  video_file = next(RAW_VIDEO_DIR.glob(f"{video_id}.*"), None)
  if video_file:
    video.update({
        "filename": video_file.name,
        "media_url": f"/media/{video_file.name}",
        "title": video_id.rsplit("_S", 1)[0].replace("-", " "),
        "episode": f"Episode {video_id.rsplit('_Ep-', 1)[-1]}",
        "status": "AI Ready",
    })
  summary = load_video_summary(video_id)
  transcript = load_video_transcript(video_id)
  return templates.TemplateResponse(
      request=request,
      name="video.html",
      context={"video": video, "summary": summary, "transcript": transcript, "format_timestamp": format_timestamp},
  )


@app.get("/summary/{video_id}", response_class=HTMLResponse, name="summary")
async def summary_view(request: Request, video_id: str):
  video = next(
      (v for v in get_videos() if str(v["id"]) == str(video_id)),
      {
          "id": video_id,
          "title": video_id.replace("-", " "),
          "episode": "Episode",
          "duration": "--:--",
      },
  )
  summary = load_video_summary(video_id)
  return templates.TemplateResponse(
      request=request,
      name="summary.html",
      context={"video": video, "summary": summary},
  )


# --- REST API Endpoints ---


@app.get("/api/videos")
async def api_get_videos():
  return get_videos()


@app.get("/api/dashboard")
async def api_get_dashboard():
  return get_dashboard_data()


@app.get("/api/summary/{video_id}")
async def api_get_summary(video_id: str):
  summary = load_video_summary(video_id)
  if not summary:
    raise HTTPException(
        status_code=404, detail="Summary not found for this video."
    )
  return summary


if __name__ == "__main__":
  import uvicorn

  uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)