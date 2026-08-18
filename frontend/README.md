# AniSense AI Frontend

Flask-ready frontend for the AI Anime Video Summarizer & Content-Based Intelligent Search project.

## Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

The frontend uses HTML5, CSS3, Vanilla JavaScript and Jinja2. Mock API routes are included and can later be replaced with the existing FastAPI/AI pipeline.

## Pages

- `/` landing page
- `/dashboard`
- `/upload`
- `/library`
- `/video/1`
- `/search`
- `/summary/1`


## Anime visual upgrade
The frontend now includes:
- AI-generated anime-fantasy atmospheric artwork
- Image-backed anime video thumbnails
- Anime-style profile avatar
- Glassmorphism cards and panels
- Floating ambient particles/petals
- Light/dark theme toggle with localStorage persistence
- Responsive mobile-safe background treatment
- Reduced-motion support
