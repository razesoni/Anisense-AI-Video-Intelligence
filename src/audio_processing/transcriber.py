from pathlib import Path
from faster_whisper import WhisperModel
import json

class AudioTranscriber:
    def __init__(self, settings, transcript_dir):
        self.model = WhisperModel(
            settings.whisper_model,
            device=settings.whisper_device,
            compute_type=settings.whisper_compute_type
        )
        self.transcripts_dir = Path(transcript_dir)

    def audio_transcribe(self, audio_path):
        audio_path = Path(audio_path)
        audio_files = [audio_path] if audio_path.is_file() else [
            file_path for file_path in audio_path.iterdir() if file_path.is_file()
        ]

        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        for audio_file in audio_files:
            transcript_file = self.transcripts_dir / f"{audio_file.stem}.json"

            segments, info = self.model.transcribe(
                str(audio_file),
                language="en",
            )
            transcript = []

            for segment in segments:
                transcript.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text, 
                })
            
            with open(str(transcript_file), "w", encoding="utf-8") as f:
                json.dump(transcript, f, ensure_ascii=False, indent=2)
            print(f"Transcription saved: {transcript_file}")



        
