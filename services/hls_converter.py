import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from .storage import storage_service

class HLSConverter:
    def __init__(self, episode):
        self.episode = episode
        self.temp_dir = tempfile.mkdtemp()
        self.mp3_path = os.path.join(self.temp_dir, "input.mp3")
        self.output_dir = os.path.join(self.temp_dir, "hls")
        os.makedirs(self.output_dir, exist_ok=True)

    def process(self):
        """
        Main flow: Download -> Convert -> Upload -> Cleanup
        """
        try:
            # 1. Download original MP3
            print(f"Downloading {self.episode.audio_file_key}...")
            if not storage_service.download_file(self.episode.audio_file_key, self.mp3_path):
                raise Exception("Failed to download MP3 from R2")

            # 2. Convert to HLS using FFmpeg
            # We use a 6-second segment time
            m3u8_filename = "playlist.m3u8"
            m3u8_path = os.path.join(self.output_dir, m3u8_filename)
            
            print("Converting to HLS...")
            command = [
                'ffmpeg', '-i', self.mp3_path,
                '-codec:', 'copy', # Copy bitstream (no re-encoding for speed)
                '-start_number', '0',
                '-hls_time', '6',
                '-hls_list_size', '0',
                '-f', 'hls', m3u8_path
            ]
            
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"FFmpeg error: {result.stderr}")

            # 3. Upload segments and playlist to R2
            # Path in R2: hls/{episode_id}/...
            r2_base_path = f"hls/{self.episode.id}"
            
            for filename in os.listdir(self.output_dir):
                file_path = os.path.join(self.output_dir, filename)
                r2_key = f"{r2_base_path}/{filename}"
                
                content_type = 'application/x-mpegURL' if filename.endswith('.m3u8') else 'video/MP2T'
                print(f"Uploading {filename} to R2...")
                storage_service.upload_file(file_path, r2_key, content_type=content_type)

            # 4. Update Episode model
            self.episode.hls_playlist_key = f"{r2_base_path}/{m3u8_filename}"
            self.episode.save()
            
            print("HLS Conversion Complete!")
            return True

        except Exception as e:
            print(f"HLS Conversion Failed: {e}")
            return False
        finally:
            # 5. Cleanup temp files
            shutil.rmtree(self.temp_dir)

def convert_episode_to_hls(episode):
    converter = HLSConverter(episode)
    return converter.process()
