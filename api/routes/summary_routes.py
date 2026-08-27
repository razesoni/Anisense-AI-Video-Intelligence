import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from config.settings import SUMMARY_DIR

router = APIRouter(prefix="/api/v1/summary", tags=["Summary"])


@router.get("/{video_id}", status_code=status.HTTP_200_OK)
async def get_summary(video_id: str):
    """
    Retrieves the generated summary JSON for a specific video ID.
    """
    summary_path = Path(SUMMARY_DIR) / f"{video_id}.json"
    if not summary_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Summary for video '{video_id}' not found."
        )
    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load summary: {e}"
        )
