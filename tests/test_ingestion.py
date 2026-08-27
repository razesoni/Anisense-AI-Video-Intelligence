import io
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_upload_invalid_extension():
    # Attempt to upload an unallowed extension (.txt)
    fake_file = io.BytesIO(b"fake text content")
    response = client.post(
        "/api/v1/ingestion/upload",
        files={"file": ("test.txt", fake_file, "text/plain")},
        data={"title": "Test Video", "season": "1", "episode": "1"},
    )
    assert response.status_code == 422
    assert "Unsupported extension" in response.json()["detail"]

def test_upload_missing_audio_or_corrupt_file():
    # Attempt to upload a corrupt or non-media file masquerading as .mp4
    fake_file = io.BytesIO(b"\x00\x00\x00\x18ftypisom")
    response = client.post(
        "/api/v1/ingestion/upload",
        files={"file": ("corrupt.mp4", fake_file, "video/mp4")}
    )
    assert response.status_code in [422, 500]