# Anisense-AI Video Intelligence
AniSense AI is an AI-powered video intelligence platform that transforms videos into searchable, structured knowledge using speech transcription, semantic search, and AI-generated summaries. It enables users to quickly find important moments, explore transcripts, and understand lengthy video content through an intuitive anime-inspired interface.

## Run the integrated application

Install the root dependencies, then run the FastAPI backend and Flask frontend in separate terminals:

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
```

```bash
pip install -r frontend/requirements.txt
python frontend/app.py
```

Open http://127.0.0.1:5000. The frontend proxies browser API requests to `http://127.0.0.1:8000`; set `ANISENSE_API_URL` to change the backend address. Uploading a video stores it in `data/raw_videos` and queues the ingestion pipeline in the backend.
