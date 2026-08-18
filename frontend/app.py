from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

VIDEOS = [
    {"id": 1, "title": "Attack on Titan", "episode": "Episode 01", "duration": "24:13", "status": "AI Ready", "segments": 182, "summary": True, "thumbnail": "aot"},
    {"id": 2, "title": "Demon Slayer", "episode": "Episode 05", "duration": "23:41", "status": "AI Ready", "segments": 164, "summary": True, "thumbnail": "demon"},
    {"id": 3, "title": "Your Name", "episode": "Movie", "duration": "1:46:12", "status": "AI Ready", "segments": 731, "summary": True, "thumbnail": "your-name"},
    {"id": 4, "title": "Jujutsu Kaisen", "episode": "Episode 12", "duration": "23:55", "status": "Processing", "segments": 0, "summary": False, "thumbnail": "jjk"},
    {"id": 5, "title": "Steins;Gate", "episode": "Episode 08", "duration": "24:02", "status": "AI Ready", "segments": 171, "summary": True, "thumbnail": "steins"},
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", videos=VIDEOS)

@app.route("/upload")
def upload():
    return render_template("upload.html")

@app.route("/library")
def library():
    return render_template("library.html", videos=VIDEOS)

@app.route("/video/<int:video_id>")
def video(video_id):
    video = next((v for v in VIDEOS if v["id"] == video_id), VIDEOS[0])
    return render_template("video.html", video=video)

@app.route("/search")
def search():
    return render_template("search.html", videos=VIDEOS)

@app.route("/summary/<int:video_id>")
def summary(video_id):
    video = next((v for v in VIDEOS if v["id"] == video_id), VIDEOS[0])
    return render_template("summary.html", video=video)

@app.get("/api/videos")
def api_videos():
    return jsonify(VIDEOS)

@app.post("/api/upload")
def api_upload():
    file = request.files.get("file")
    if not file:
        return jsonify({"success": False, "message": "No video selected."}), 400
    return jsonify({
        "success": True,
        "message": "Video uploaded successfully",
        "filename": file.filename
    })

@app.post("/api/process")
def api_process():
    return jsonify({"success": True, "message": "Processing started"})

@app.post("/api/search")
def api_search():
    payload = request.get_json(silent=True) or {}
    query = payload.get("query", "").strip()
    results = [
        {
            "video": "Attack on Titan — Episode 03",
            "time": "12:43",
            "match": 94,
            "snippet": "...the commander reveals that the walls were built to protect humanity from..."
        },
        {
            "video": "Demon Slayer — Episode 05",
            "time": "08:17",
            "match": 89,
            "snippet": "...the mysterious girl finally appears and the protagonist realizes she knows..."
        },
        {
            "video": "Steins;Gate — Episode 08",
            "time": "17:26",
            "match": 84,
            "snippet": "...the conversation changes everything as the hidden message is decoded..."
        },
    ]
    return jsonify({"query": query, "results": results})

@app.get("/api/summary/<int:video_id>")
def api_summary(video_id):
    return jsonify({
        "overview": "The episode follows a tense sequence of events as the main characters uncover new information, face a growing conflict, and make a difficult decision.",
        "key_points": [
            "Main event and setup",
            "Character development",
            "Important dialogue",
            "Major conflict",
            "Important revelation"
        ],
        "topics": ["Battle", "Friendship", "Character Development", "Mystery", "Conflict"]
    })

if __name__ == "__main__":
    app.run(debug=True)
