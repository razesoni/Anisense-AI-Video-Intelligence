"""FastAPI router endpoints for semantic search operations."""

import logging
from typing import Optional

from api.schemas.search import SearchRequest, SearchResponse
from fastapi import APIRouter, HTTPException, Query, status
from pipelines.search_pipeline import SearchPipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["search"])

# Singleton pipeline instance initialized lazily
_search_pipeline: Optional[SearchPipeline] = None


def get_search_pipeline() -> SearchPipeline:
    """Returns or initializes the SearchPipeline singleton instance."""
    global _search_pipeline
    if _search_pipeline is None:
        _search_pipeline = SearchPipeline()
    return _search_pipeline


@router.post("/search", response_model=SearchResponse, status_code=status.HTTP_200_OK)
async def perform_search_post(payload: SearchRequest) -> SearchResponse:
    """Performs semantic video search across transcript segments and anime summaries (POST endpoint).

    Args:
        payload: SearchRequest object containing query, top_k, scope, and filters.

    Returns:
        SearchResponse payload containing matching result hits and metrics.
    """
    try:
        pipeline = get_search_pipeline()
        results = pipeline.run_search(
            query=payload.query,
            top_k=payload.top_k,
            search_scope=payload.scope,
            filters=payload.filters,
        )
        return SearchResponse(**results)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        )
    except Exception as err:
        logger.exception(f"Unhandled error during search execution: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while executing search: {str(err)}",
        )


@router.get("/search", response_model=SearchResponse, status_code=status.HTTP_200_OK)
async def perform_search_get(
    q: str = Query(..., min_length=1, max_length=500, description="Search query string"),
    top_k: int = Query(default=4, ge=1, le=50, description="Top k results to return"),
    scope: str = Query(default="both", description="Search target scope ('transcript', 'summary', or 'both')"),
) -> SearchResponse:
    """Performs semantic video search across transcript segments and anime summaries (GET endpoint)."""
    return await perform_search_post(SearchRequest(query=q, top_k=top_k, scope=scope))
