import json
from pathlib import Path
from groq import Groq

class AudioTranscriber:
    def __init__(self, settings, transcript_dir):
        self.provider = getattr(settings, "transcription_provider").lower()
        self.api_key = getattr(settings, "groq_api_key", None)
        self.client = Groq(api_key=self.api_key) if self.api_key else Groq()
        self.model_name = getattr(settings, "groq_model", "whisper-large-v3")
        self.transcripts_dir = Path(transcript_dir)

    def audio_transcribe(self, audio_path):
        audio_path = Path(audio_path)
        audio_files = [audio_path] if audio_path.is_file() else [
            file_path for file_path in audio_path.iterdir() if file_path.is_file()
        ]

        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        for audio_file in audio_files:
            transcript_file = self.transcripts_dir / f"{audio_file.stem}.json"
            transcript = self._transcribe_groq(audio_file)
            
            with open(str(transcript_file), "w", encoding="utf-8") as f:
                json.dump(transcript, f, ensure_ascii=False, indent=2)
            print(f"Transcription saved: {transcript_file}")
            

    def _transcribe_groq(self, audio_file):
        with open(audio_file, "rb") as file:
            response = self.client.audio.transcriptions.create(
                file=(audio_file.name, file.read()),
                model=self.model_name,
                language="en",
                response_format="verbose_json"
            )
        
        transcript = []
        segments = getattr(response, "segments", [])
        for segment in segments:
            # Access dictionary key or attribute depending on returned object format
            start = segment.get("start") if isinstance(segment, dict) else getattr(segment, "start", 0)
            end = segment.get("end") if isinstance(segment, dict) else getattr(segment, "end", 0)
            text = segment.get("text") if isinstance(segment, dict) else getattr(segment, "text", "")
            transcript.append({"start": start, "end": end, "text": text})
            
        return transcript