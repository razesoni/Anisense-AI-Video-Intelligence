import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from api.main import app
from config.settings import SUMMARY_DIR
from src.summarisation.prompts import (
    batch_transcript_chunks,
    format_map_prompt,
    format_reduce_prompt,
)
from src.summarisation.parser import (
    parse_summary_output,
    parse_map_output,
    generate_fallback_summary,
    SummaryResponse,
    MapSegmentOutput,
)
from pipelines.ingestion_pipeline_ import IngestionPipeline

client = TestClient(app)


def test_batch_transcript_chunks():
    chunks = [{"start": i*5.0, "end": (i+1)*5.0, "text": f"Line {i}"} for i in range(120)]
    batches = batch_transcript_chunks(chunks, batch_size=50)
    assert len(batches) == 3
    assert "[0.0s - 5.0s] Line 0" in batches[0]
    assert "[250.0s - 255.0s] Line 50" in batches[1]
    assert "[500.0s - 505.0s] Line 100" in batches[2]


def test_parse_map_output_valid():
    raw_response = """
    ```json
    {
        "segment_summary": "Intro dialogue segment",
        "local_key_points": ["Character A greets B"],
        "notable_moments": [
            {"timestamp_start": 0.0, "timestamp_end": 10.0, "label": "Greeting", "description": "Character arrival"}
        ]
    }
    ```
    """
    parsed = parse_map_output(raw_response)
    assert parsed is not None
    assert parsed.segment_summary == "Intro dialogue segment"
    assert parsed.local_key_points == ["Character A greets B"]
    assert len(parsed.notable_moments) == 1
    assert parsed.notable_moments[0].label == "Greeting"


def test_parse_summary_output_valid():
    raw_response = """
    ```json
    {
        "overview": "Test overview",
        "key_points": ["Point 1", "Point 2"],
        "key_moments": [
            {"timestamp_start": 0.0, "timestamp_end": 10.0, "label": "Opening", "description": "Intro scene"}
        ],
        "tags": ["Action", "Anime"]
    }
    ```
    """
    parsed = parse_summary_output(raw_response)
    assert parsed is not None
    assert parsed.overview == "Test overview"
    assert len(parsed.key_points) == 2
    assert len(parsed.key_moments) == 1
    assert parsed.tags == ["Action", "Anime"]


def test_parse_summary_output_truncated_repair():
    raw_response = '{"overview": "Truncated overview", "key_points": ["Point 1"], "key_moments": [{"timestamp_start": 0.0, "timestamp_end": 5.0, "label": "Start", "description": "Intro"}'
    parsed = parse_summary_output(raw_response)
    assert parsed is not None
    assert parsed.overview == "Truncated overview"


def test_generate_fallback_summary():
    chunks = [
        {"start": 0.0, "end": 5.0, "text": "Welcome to Episode 1 of the series."},
        {"start": 5.0, "end": 12.0, "text": "The main character enters the classroom."},
        {"start": 12.0, "end": 20.0, "text": "A surprise exam is announced by the teacher."}
    ]
    fallback = generate_fallback_summary(chunks, media_title="Test_Anime_S1_Ep-01")
    assert isinstance(fallback, SummaryResponse)
    assert "Test Anime S1 Ep 01" in fallback.overview or "Test Anime" in fallback.overview
    assert len(fallback.key_moments) > 0
    assert len(fallback.tags) > 0


def test_summary_api_endpoint(tmp_path):
    test_video_id = "Test-Video_S1_Ep-99"
    summary_data = {
        "overview": "API test overview",
        "key_points": ["API Point"],
        "key_moments": [],
        "tags": ["API Test"]
    }
    
    summary_file = Path(SUMMARY_DIR) / f"{test_video_id}.json"
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary_data, f)
        
    try:
        response = client.get(f"/api/v1/summary/{test_video_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["overview"] == "API test overview"
    finally:
        if summary_file.exists():
            summary_file.unlink()
