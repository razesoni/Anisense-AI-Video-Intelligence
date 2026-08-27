# AniSense AI — Video Intelligence

AniSense AI is an AI-powered video intelligence platform that transforms videos into searchable, structured knowledge using speech transcription, semantic search, and AI-generated summaries. It helps users quickly find important moments, explore transcripts, and understand lengthy video content through an intuitive anime-inspired interface.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Languages](https://img.shields.io/github/languages/top/razesoni/Anisense-AI-Video-Intelligence)](https://github.com/razesoni/Anisense-AI-Video-Intelligence)
[![Repo size](https://img.shields.io/github/repo-size/razesoni/Anisense-AI-Video-Intelligence)](https://github.com/razesoni/Anisense-AI-Video-Intelligence)

Status: WIP / Beta

---

## Table of contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Quickstart (local development)](#quickstart-local-development)
- [Configuration](#configuration)
- [Usage](#usage)
- [Testing & linting](#testing--linting)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [License & contact](#license--contact)

---

## Features

- Time-aligned speech transcription from uploaded videos
- Semantic search across transcripts using embeddings + vector DB
- AI-generated summaries and highlights for video segments
- Interactive transcript viewer with jump-to-video timestamps
- Anime-inspired UI with responsive design and accessibility considerations
- Modular ingestion pipeline (audio extraction, chunking, ASR, embedding)

---

## Architecture

High-level pipeline:

1. Ingest — upload video via frontend or API
2. Preprocess — extract audio (ffmpeg), split into chunks
3. Transcription — ASR model produces time-aligned transcripts
4. Enrichment — generate embeddings per segment and store them in a vector DB
5. Search & Summarization — semantic search and LLM-based summaries
6. Frontend — UI for browsing transcripts, searching, and viewing highlights

Repository layout (high level):

- api/ — FastAPI backend (entry: `api.main:app`)
- frontend/ — Flask-based frontend (entry: `frontend/app.py`)
- data/ — local data and sample storage
- scripts/ — helper scripts for processing, ingestion, and maintenance

(Adjust paths above to match actual layout in the repo if they differ.)

---

## Tech stack

- Backend: Python, FastAPI, Uvicorn
- Frontend: Flask, Jinja2, Vanilla JavaScript, HTML/CSS
- ML: ASR (e.g., Whisper or alternative), embeddings, LLM summarization
- Media tooling: ffmpeg for audio/video processing
- Vector DB: pluggable (FAISS / Pinecone / Milvus / etc.)
- Containerization/orchestration: Docker, Docker Compose, Kubernetes (optional)

---

## Prerequisites

- Python 3.9+ (3.10+ recommended)
- ffmpeg (installed and available on PATH)
- Git
- (Optional) Docker & Docker Compose
- (Optional) Node.js & npm if adding a JS build step for frontend

---

## Quickstart (local development)

Clone the repository:

```bash
git clone https://github.com/razesoni/Anisense-AI-Video-Intelligence.git
cd Anisense-AI-Video-Intelligence
```

Create and activate a virtual environment

macOS / Linux
```bash
python -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies (root/backend):

```bash
pip install -r requirements.txt
```

Start the backend (FastAPI + Uvicorn):

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Start the frontend (Flask):

```bash
pip install -r frontend/requirements.txt
python frontend/app.py
```

Open the UI at http://127.0.0.1:5000. The frontend proxies API requests to `http://127.0.0.1:8000` by default; override with the `ANISENSE_API_URL` environment variable if required.

---

## Configuration

Create a `.env` file at the project root or set environment variables in your environment. Common variables:

- ANISENSE_API_URL — backend API URL (frontend proxy)
- STORAGE_PATH — local path or cloud bucket for uploaded videos (default: `data/`)
- VECTOR_DB_URL — connection string for vector DB (if used)
- OPENAI_API_KEY — API key for embeddings/LLM services (optional)
- DATABASE_URL — SQL/NoSQL database connection (optional)
- SECRET_KEY — Flask/Session secret
- FFMPEG_PATH — custom path to ffmpeg if not on PATH

Example .env:
```env
ANISENSE_API_URL=http://127.0.0.1:8000
STORAGE_PATH=./data
OPENAI_API_KEY=sk-...
DATABASE_URL=sqlite:///data/db.sqlite3
SECRET_KEY=replace-with-a-secret
```

---

## Usage

Typical flow:
1. Upload a video via web UI or API.
2. Ingestion pipeline extracts audio and chunks it for ASR.
3. Backend saves time-aligned transcripts and metadata.
4. Embeddings are generated for segments and stored in the vector DB.
5. Use the UI search to find moments or view AI-generated summaries.

Example upload (adjust endpoint/auth as appropriate):
```bash
curl -X POST "$ANISENSE_API_URL/api/videos/upload" \
  -H "Authorization: Bearer $API_TOKEN" \
  -F "file=@/path/to/video.mp4"
```

---

## Testing & linting

- Run tests: pytest
- Formatting: black
- Linting: flake8 / pylint
- Add end-to-end tests for ingestion/transcription/embedding flows.

---

## Deployment

Recommended approaches:

- Dockerize backend and frontend; use Docker Compose for local testing and Kubernetes for production.
- Host frontend statically (if converted to SPA) on Vercel/Netlify; host backend on Cloud Run / ECS / EKS.
- Use S3-compatible storage for large video files.
- Use a managed vector DB for scale (Pinecone, Milvus Cloud).

Example (outline):
```bash
docker build -t anisense-backend -f Dockerfile.backend .
docker build -t anisense-frontend -f frontend/Dockerfile .
```

---

## Contributing

Contributions welcome!

1. Fork the repo and create a branch: `git checkout -b feat/your-feature`
2. Add tests and documentation
3. Open a pull request explaining the change and motivation

Suggested labels: bug, enhancement, docs. Consider adding `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` for external contributions.

---

## Roadmap

- Real-time / streaming transcription & indexing
- Multi-language support and translation pipeline
- Improved speaker diarization and speaker labeling
- Chapter-style structured summaries and highlights
- User editing and annotation tools for transcripts

---

## License & contact

This project is available under the MIT License — see [LICENSE](LICENSE) for details.

Maintainer: razesoni — open issues or PRs at https://github.com/razesoni/Anisense-AI-Video-Intelligence
