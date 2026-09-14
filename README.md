# AniSense AI — Video Intelligence Platform

**AniSense AI** is a comprehensive AI-powered video intelligence platform that transforms videos into structured, searchable knowledge through automated transcription, semantic search, and AI-generated summaries. Built with a modular architecture, it enables users to quickly locate important moments, explore full transcripts, and understand lengthy video content through an intuitive anime-inspired web interface.

## Key Features

- **Speech-to-Text Transcription**: Leverages OpenAI's Whisper model with optimized inference for CPU-based processing
- **Semantic Search**: Hybrid retrieval combining vector embeddings (Chroma) and BM25 keyword indexing with cross-encoder re-ranking
- **AI Summaries**: Multi-stage summarization pipeline (Map-Reduce architecture) using local LLM inference (Ollama) with optional Google Gemini integration
- **Timestamped Insights**: Automatic extraction of key moments with timestamps for quick navigation
- **Web Interface**: FastAPI-powered REST API with Jinja2 templated frontend for dashboard, library, search, and analytics views
- **Production-Ready Validation**: Comprehensive video codec validation, file size enforcement, and error handling

## Tech Stack

### Backend
- **Framework**: FastAPI 0.115+ with Uvicorn ASGI server
- **Data Processing**: Pydantic (schemas & validation), Python-Dotenv (config)
- **Audio/Video**: FFmpeg (media extraction), faster-whisper (transcription), spaCy (text normalization)
- **Search & Indexing**: 
  - ChromaDB (persistent vector storage with embedding model: sentence-transformers/all-MiniLM-L6-v2)
  - Rank-BM25 (keyword-based retrieval)
  - Sentence-Transformers (cross-encoder re-ranking)
- **LLM Integration**: Ollama (local inference), Google Generative AI (optional cloud-based fallback)

### Frontend
- **Templating**: Jinja2 templates served by FastAPI
- **Static Assets**: CSS, JavaScript (anime-inspired design)
- **API Communication**: Fetch API with REST endpoints

### Infrastructure
- **Local-First Design**: All processing runs on-device; models downloaded locally
- **Environment Configuration**: `.env`-based settings with Pydantic BaseSettings

---

## Project Structure

```
.
├── api/                         # FastAPI application server
│   ├── main.py                  # Entry point: routes, middleware, dashboard logic
│   ├── routes/                  # REST API endpoints
│   │   ├── ingestion_routes.py  # Video upload, background job processing
│   │   ├── search_routes.py     # Semantic search endpoints (GET/POST)
│   │   └── summary_routes.py    # Summary retrieval endpoints
│   └── schemas/                 # Pydantic request/response models
│       ├── search.py            # SearchRequest, SearchResult, SearchResponse
│       └── video.py             # Upload, ingestion status schemas
│
├── config/                      # Application configuration
│   └── settings.py              # Pydantic BaseSettings with environment variables
│
├── pipelines/                   # High-level orchestration
│   ├── ingestion_pipeline_.py   # Audio extraction → transcription → indexing → summarization
│   └── search_pipeline.py       # Query processing → retrieval → ranking → enrichment
│
├── src/                         # Core processing modules
│   ├── audio_processing/        # Audio extraction and transcription
│   │   ├── extractor.py         # FFmpeg-based audio extraction
│   │   └── transcriber.py       # Whisper-based transcription
│   ├── transcript_cleaning/     # Text normalization and segmentation
│   │   ├── cleaner.py           # Transcript deduplication & cleanup
│   │   ├── normalizer.py        # spaCy-based text normalization
│   │   └── segmenter.py         # Chunk-based segmentation with timestamps
│   ├── indexing/                # Vector and keyword indexing
│   │   ├── vector_db.py         # ChromaDB persistent collection management
│   │   └── summary_indexing.py  # Summary-specific vector indexing
│   ├── search/                  # Advanced retrieval & ranking
│   │   ├── query_processor.py   # Query sanitization and filter construction
│   │   ├── similarity_engine.py # Two-stage retrieval (bi-encoder + cross-encoder)
│   │   ├── keyword_db.py        # BM25Okapi keyword search
│   │   └── snippet_extractor.py # Result merging and timestamp formatting
│   ├── summarisation/           # LLM-based summarization
│   │   ├── llm_client.py        # Ollama/Gemini client abstraction
│   │   ├── prompts.py           # Map-Reduce prompt templates
│   │   └── parser.py            # JSON response parsing with repair logic
│   └── ingestion/               # Video upload and validation
│       ├── uploader.py          # Canonical filename formatting & file I/O
│       └── validator.py         # Codec, size, format validation
│
├── frontend/                    # Web interface
│   ├── templates/               # Jinja2 HTML templates
│   │   ├── index.html           # Home page
│   │   ├── dashboard.html       # Analytics dashboard
│   │   ├── upload.html          # Video upload form
│   │   ├── library.html         # Video library browser
│   │   ├── search.html          # Semantic search interface
│   │   ├── video.html           # Video player with transcript
│   │   └── summaries.html       # Summary viewer
│   └── static/                  # CSS, JavaScript, images, icons
│
├── tests/                       # Unit tests
│   └── test_segmenter.py        # Isolated segmentation tests (no ML models)
│
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Development dependencies
├── .env.example                 # Configuration template
└── .gitignore                   # Exclude data/ and runtime artifacts
```

---

## How It Works

### 1. **Ingestion Pipeline**
1. **Upload**: FastAPI endpoint accepts video file with title/season/episode metadata
2. **Validation**: Verify file format, codecs, and size constraints
3. **Audio Extraction**: FFmpeg extracts mono 16kHz audio stream
4. **Transcription**: faster-whisper converts audio to timestamped segments
5. **Cleaning**: Text normalization (spaCy), deduplication, chunk segmentation
6. **Indexing**: Segments indexed into ChromaDB (vector) and BM25 (keyword)
7. **Summarization**: Map-Reduce pipeline generates structured summaries via LLM

### 2. **Search Pipeline**
1. **Query Processing**: Sanitize and normalize user input, build metadata filters
2. **Bi-Encoder Retrieval**: ChromaDB vector search across transcript segments and summaries
3. **Cross-Encoder Re-ranking**: Sentence-Transformers re-rank candidates by semantic relevance
4. **Snippet Extraction**: Merge overlapping results, format timestamps
5. **Metadata Enrichment**: Attach video title, episode, media URLs
6. **Response**: Return ranked results with confidence scores and watch links

### 3. **API & UI**
- **Dashboard**: Aggregates processing stats (videos, total duration, summaries, indexed segments)
- **Library**: Browse ingested videos with status indicators
- **Video Player**: Stream video with synced transcript and clickable timestamps
- **Search Interface**: Free-form natural language queries with filtering
- **Summaries**: View structured key moments, tags, and takeaways
- **Analytics**: Placeholder for future engagement/quality metrics

---

## Quick Start

### Prerequisites
- **Python 3.11+** in a virtual environment
- **FFmpeg** and **FFprobe** on PATH (for media processing)
- **Ollama** installed and running separately (for local LLM inference)

### Installation

```bash
# Clone and install dependencies
git clone https://github.com/razesoni/Anisense-AI-Video-Intelligence.git
cd Anisense-AI-Video-Intelligence

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -m pip install -r requirements.txt

# Download NLP and ML models
python -m spacy download en_core_web_sm
ollama pull qwen3:4b  # Or your preferred model
```

### Configuration

```bash
# Copy example environment and adjust for your machine
cp .env.example .env
```

Edit `.env` to match your setup:
```env
WHISPER_MODEL=base              # tiny, base, small, medium, large
WHISPER_DEVICE=cpu              # cpu or cuda
WHISPER_COMPUTE_TYPE=int8       # int8, int16, float32
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen3:4b           # or any Ollama-compatible model
SUMMARY_PROVIDER=ollama         # ollama or gemini
MAX_FILE_SIZE_MB=200
# Optional: GEMINI_API_KEY=xxx for cloud-based summaries
```

### Run the Application

```bash
# Start the FastAPI server
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Access:
- **Web UI**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Example Workflow

1. Navigate to **Upload** page
2. Select a video file (MP4, MKV, WebM, etc.)
3. Enter series title, season, and episode number
4. Submit – ingestion runs in the background
5. View **Dashboard** or **Library** for processing status
6. Once complete, use **Search** to query video content semantically
7. Click results to jump to specific timestamps in the **Video** viewer

---

## API Endpoints

### Ingestion
- `POST /api/v1/ingestion/upload` – Upload video and start background processing
- `GET /api/v1/ingestion/status/{job_id}` – Poll ingestion job status

### Search
- `POST /api/search` – Semantic search (request body with query, top_k, scope)
- `GET /api/search?q=query&top_k=4&scope=both` – Semantic search (query params)

### Summaries
- `GET /api/v1/summary/{video_id}` – Retrieve structured summary (overview, key points, key moments, tags)

### Data
- `GET /api/videos` – List all ingested videos
- `GET /api/dashboard` – Dashboard statistics

---

## Configuration Guide

All settings are defined in `config/settings.py` and can be overridden via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `WHISPER_MODEL` | `base` | Whisper model size (tiny, base, small, medium, large) |
| `WHISPER_DEVICE` | `cpu` | Inference device (cpu, cuda) |
| `WHISPER_COMPUTE_TYPE` | `int8` | Quantization (int8, int16, float32) |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server endpoint |
| `OLLAMA_MODEL` | `qwen3:4b` | LLM model name in Ollama |
| `SUMMARY_PROVIDER` | `ollama` | Summary backend (ollama, gemini) |
| `GEMINI_API_KEY` | (none) | Google Gemini API key (if using Gemini) |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model version |
| `MAX_FILE_SIZE_MB` | `200` | Maximum upload size |
| `embedding_model` | `all-MiniLM-L6-v2` | Sentence-Transformers embedding model |

---

## Testing

Run isolated segmentation tests (no model downloads required):

```bash
python -m unittest discover -s tests -p test_segmenter.py -v
```

**Note**: Full ingestion and summarization tests require the complete runtime (Whisper models, Ollama, ChromaDB) and are not executed in CI.

---

## Known Limitations

- **Language**: Transcription enforces English; auto-detection and translation not yet implemented
- **Authentication**: No user auth or role-based access control
- **Evaluation**: End-to-end retrieval evaluation (Recall@k, NDCG) not yet benchmarked
- **Embedding Customization**: ChromaDB defaults to built-in embeddings; custom embedders require code modification
- **Summary Accuracy**: LLM-generated summaries may hallucinate or misrepresent source content – always cross-check with transcript
- **Admin Features**: Some admin modules remain stubs

---

## Roadmap

- [ ] Small labeled evaluation set for retrieval quality metrics (Recall@k, MRR, NDCG)
- [ ] Latency and throughput benchmarking
- [ ] Automatic language detection with optional translation
- [ ] Corrupted media handling and edge-case testing
- [ ] Public demo deployment with shareable media samples
- [ ] Basic authentication and user sessions
- [ ] Analytics dashboard with engagement metrics
- [ ] Support for other media types (podcasts, lectures, streams)

---

## Legal & Attribution

This repository uses anime-inspired character artwork and styling for educational and demonstration purposes. All third-party media and artwork retain their respective intellectual property rights. This project does not grant a blanket license to those assets.

---

## Technologies & Stack

**Core ML/AI**: Whisper, ChromaDB, Sentence-Transformers, Ollama, spaCy, Rank-BM25  
**Backend**: FastAPI, Python 3.11+, Pydantic  
**Frontend**: Jinja2, HTML/CSS/JavaScript  
**Infrastructure**: FFmpeg, SQLite (ChromaDB), local file storage  
**Development**: pytest, Python unittest  

---

## Contact & Collaboration

For questions, feature requests, or collaboration opportunities, please open an issue or pull request on GitHub.
