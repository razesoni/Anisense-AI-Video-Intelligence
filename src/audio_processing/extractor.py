from pathlib import Path
import subprocess

class AudioExtractor:
    def __init__(self, settings, audio_dir):
        self.settings = settings
        self.audio_dir = Path(audio_dir)

        self.audio_format = settings.audio_format
        self.audio_sample_rate = settings.audio_sample_rate
        self.audio_channels = settings.audio_channels
        
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    def extract_audio(self, video_path):
        video_path = Path(video_path)
        video_files = [video_path] if video_path.is_file() else [
            file_path for file_path in video_path.iterdir() if file_path.is_file()
        ]


        for video_file in video_files:
            audio_file = self.audio_dir / f"{video_file.stem}.mp3"
            print(f"Converting{video_file.name} -> {audio_file.name}")

            command = [
                "ffmpeg",
                "-y", 
                "-i", str(video_file),
                # Remove video stream
                "-vn",
                # MP3 codec
                "-c:a", "libmp3lame",
                # Audio quality
                "-b:a", "192k",
                # Mono
                "-ac", str(self.audio_channels),
                # Sample rate
                "-ar", str(self.audio_sample_rate),
                str(audio_file)
            ]

            try:
                subprocess.run(command, check=True)
                print(f"Success: {audio_file.name}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to convert {video_file.name}: {e}")
    
    
        

