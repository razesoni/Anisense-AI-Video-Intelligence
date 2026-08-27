from datetime import datetime, timezone
from fastapi import APIRouter, BackgroundTasks, UploadFile, File, Form, HTTPException, status
from pathlib import Path
from src.ingestion.uploader import VideoUploader, format_canonical_filename
from api.schemas.video import IngestionJobResponse, IngestionStatusResponse
from pipelines.ingestion_pipeline_ import IngestionPipeline


router = APIRouter(prefix="/api/v1/ingestion", tags=["Ingestion"])
uploader = VideoUploader()
video_processing = IngestionPipeline()
jobs = {}

STAGES = {
    "validation": "done",
    "audio": "pending",
    "transcription": "pending",
    "cleaning": "pending",
    "indexing": "pending",
    "summarization": "pending",
}


def process_job(job_id, saved_path):
    jobs[job_id]["status"] = "processing"

    def update_stage(stage, state):
        jobs[job_id]["current_stage"] = stage
        jobs[job_id]["stages"][stage] = state

    try:
        result = video_processing.run(saved_path, progress_callback=update_stage)
        jobs[job_id].update(status="completed", message="Video ingestion completed.", result=result)
    except Exception as error:
        current_stage = jobs[job_id].get("current_stage")
        if current_stage:
            jobs[job_id]["stages"][current_stage] = "error"
        jobs[job_id].update(status="failed", message=f"Ingestion failed: {error}")

@router.post("/upload", response_model=IngestionJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(..., description="Name/Series title, e.g., Classroom of the Elite"),
    season: int = Form(..., ge=1, description="Season number, e.g., 1"),
    episode: int = Form(..., ge=1, description="Episode number, e.g., 6")
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing file.")

    original_filename = file.filename

    # Generate the standardized filename
    canonical_filename = format_canonical_filename(
        title=title,
        season=season,
        episode=episode,
        original_filename=original_filename
    )

    try:
        # Pass the formatted filename to be saved
        video_id, saved_path, metadata = uploader.save_and_validate(
            file_stream=file.file,
            canonical_filename=canonical_filename
        )

        job_id = video_id
        jobs[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "current_stage": "validation",
            "stages": dict(STAGES),
            "message": "Video uploaded. Ingestion is starting.",
            "result": None,
            "video": {
                "id": job_id,
                "title": title,
                "episode": f"Episode {episode:02d}",
                "duration": f"{int(metadata.duration_seconds // 60):02d}:{int(metadata.duration_seconds % 60):02d}",
                "filename": canonical_filename,
            },
            "created_at": datetime.now(timezone.utc),
        }
        background_tasks.add_task(process_job, job_id, saved_path)
        return IngestionJobResponse(
            job_id=job_id,
            status="queued",
            message="Video uploaded. Ingestion is starting.",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ingestion failed: {str(e)}")


@router.get("/status/{job_id}", response_model=IngestionStatusResponse)
async def ingestion_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Ingestion job not found.")
    return job