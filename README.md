# AniSense AI — Video Intelligence

A local Python application for turning videos into timestamped transcripts, searchable segments, and generated summaries. The anime-inspired interface is served by **FastAPI with Jinja2 templates**.

**Status:** development prototype. Retrieval quality, summary faithfulness, and processing latency have not yet been benchmarked.

## Implemented architecture

Video upload → validation / FFmpeg extraction → faster-whisper transcription → transcript cleaning → Chroma indexing → search and LLM summaries.

| Directory | Responsibility |
| --- | --- |
| `api/` | FastAPI application, routes, schemas, and HTML views |
| `config/` | Settings and storage paths |
| `pipelines/` | Ingestion and search orchestration |
| `src/` | Validation, audio, cleaning, indexing, retrieval, summarization |
| `frontend/` | Jinja2 templates and static assets |
| `tests/` | Existing ingestion and summarization tests |

## Local setup

Use Python 3.11 in a virtual environment. Install FFmpeg and ensure both `ffmpeg` and `ffprobe` are on PATH. Install and start Ollama separately.

```bash
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm
ollama pull qwen3:4b
```

Copy `.env.example` to `.env` and adjust model choices for your machine. Model downloads require network access. CPU processing can be slow; start with a short English video.

```bash
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Open [the local UI](http://127.0.0.1:8000) and [interactive API documentation](http://127.0.0.1:8000/docs). A separate Flask frontend process is not required.

Upload a short video through the UI, inspect its transcript, then test search and summary output. Generated media, transcripts and indexes are local runtime data and are excluded from Git.

## Configuration

`config/settings.py` is the source of truth. The example environment matches its fields:
- `WHISPER_MODEL`, `WHISPER_DEVICE`, `WHISPER_COMPUTE_TYPE`
- `OLLAMA_HOST`, `OLLAMA_MODEL`, `SUMMARY_PROVIDER`
- Optional `GEMINI_API_KEY` / `GEMINI_MODEL`
- `MAX_FILE_SIZE_MB`

## Validation

```bash
python -m unittest discover -s tests -p test_segmenter.py -v
```

The segmenter tests check empty input, distinct chunk identifiers, and timestamps without model downloads. Existing ingestion and summarization tests require the full runtime and local NLP resources. CI runs the isolated segmenter tests; it does not certify the full media pipeline.

## Known limitations

- Transcription currently requests English explicitly; automatic language detection and translation are not implemented.
- There is no authentication implementation or production deployment configuration.
- Some admin modules remain placeholders.
- Search/transcription end-to-end evaluation remains to be added.
- Chroma uses its collection embedding behavior; the settings field alone does not establish a custom embedding function.
- Generated summaries may be incorrect; compare them with the source transcript.

## Next milestones

Add a small labeled retrieval evaluation set, measure Recall@k and query latency, test corrupt media deterministically, and publish a short demonstration using media with permission to share.

Third-party character artwork and media retain their respective rights. This repository does not grant a blanket license to those assets.
