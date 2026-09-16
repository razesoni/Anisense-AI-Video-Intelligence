# AniSense AI — Video Intelligence Platform

**AniSense AI** is a comprehensive AI-powered video intelligence platform that transforms videos into structured, searchable knowledge through automated transcription, semantic search, and AI-generated summaries powered by Groq and Gemini.

## Key Features

- **Speech-to-Text Transcription**: Leverages Groq's fast inference APIs for transcription and optional Gemini-powered analysis workflows
- **Semantic Search**: Hybrid retrieval combining vector embeddings (Chroma) and BM25 keyword indexing with cross-encoder re-ranking
- **AI Summaries**: Multi-stage summarization pipeline (Map-Reduce architecture) using Groq and Gemini models for high-velocity, cloud-backed generation
- **Timestamped Insights**: Automatic extraction of key moments with timestamps for quick navigation
- **Web Interface**: FastAPI-powered REST API with Jinja2 templated frontend for dashboard, library, search, and analytics views
- **Production-Ready Validation**: Comprehensive video codec validation, file size enforcement, and error handling

## Tech Stack

### Backend
- **Framework**: FastAPI 0.115+ with Uvicorn ASGI server
- **Data Processing**: Pydantic (schemas & validation), Python-Dotenv (config)
- **Audio/Video**: FFmpeg (media extraction), Groq API for transcription and inference, spaCy (text normalization)
- **Search & Indexing**:
  - ChromaDB (persistent vector storage with embedding model: sentence-transformers/all-MiniLM-L6-v2)
  - Rank-BM25 (keyword-based retrieval)
  - Sentence-Transformers (cross-encoder re-ranking)
- **LLM Integration**: Groq (high-speed cloud inference), Google Generative AI / Gemini (cloud-based summarization and fallback)

### Frontend
- **Templating**: Jinja2 templates served by FastAPI
- **Static Assets**: CSS, JavaScript (anime-inspired design)
- **API Communication**: Fetch API with REST endpoints

### Infrastructure
- **Cloud-First AI Layer**: Groq and Gemini API keys drive processing and summarization workflows
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
│   │   └── transcriber.py       # Groq/Gemini-backed transcription integration
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
│   │   ├── llm_client.py        # Groq/Gemini client abstraction
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
4. **Transcription**: Groq-based transcription converts audio to timestamped segments
5. **Cleaning**: Text normalization (spaCy), deduplication, chunk segmentation
6. **Indexing**: Segments indexed into ChromaDB (vector) and BM25 (keyword)
7. **Summarization**: Map-Reduce pipeline generates structured summaries via Groq or Gemini LLMs

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
- **Groq API key** for transcription/inference
- **Google Gemini API key** for cloud-based summarization fallback

### Installation

```bash
# Clone and install dependencies
git clone https://github.com/razesoni/Anisense-AI-Video-Intelligence.git
cd Anisense-AI-Video-Intelligence

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -m pip install -r requirements.txt

# Download NLP models
python -m spacy download en_core_web_sm
```

### Configuration

```bash
# Copy example environment and adjust for your machine
cp .env.example .env
```

Edit `.env` to match your setup:
```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile   # or other Groq-compatible model
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
SUMMARY_PROVIDER=gemini             # groq or gemini
MAX_FILE_SIZE_MB=200
# Optional: adjust custom embedding model if needed
# embedding_model=all-MiniLM-L6-v2
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
| `GROQ_API_KEY` | (none) | Groq API key for transcription and inference |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model used for summarization/inference |
| `GEMINI_API_KEY` | (none) | Google Gemini API key |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model version |
| `SUMMARY_PROVIDER` | `gemini` | Summary backend (`groq`, `gemini`) |
| `MAX_FILE_SIZE_MB` | `200` | Maximum upload size |
| `embedding_model` | `all-MiniLM-L6-v2` | Sentence-Transformers embedding model |

---

## Testing

Run isolated segmentation tests (no model downloads required):

```bash
python -m unittest discover -s tests -p test_segmenter.py -v
```

**Note**: Full ingestion and summarization tests require the complete runtime (Groq/Gemini credentials, ChromaDB, and model dependencies) and are not executed in CI.

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

This repository uses anime-inspired character artwork and styling for educational and demonstration purposes. All third-party media and artwork retain their respective intellectual property rights. The platform is intended for research, experimentation, and local deployment scenarios only.

---

## Technologies & Stack

**Core ML/AI**: Groq, Gemini, ChromaDB, Sentence-Transformers, spaCy, Rank-BM25  
**Backend**: FastAPI, Python 3.11+, Pydantic  
**Frontend**: Jinja2, HTML/CSS/JavaScript  
**Infrastructure**: FFmpeg, SQLite (ChromaDB), cloud API integrations  
**Development**: pytest, Python unittest  

---

## Contact & Collaboration

For questions, feature requests, or collaboration opportunities, please open an issue or pull request on GitHub.
