"""
Junay 4K Downloader - Flask Web App
Beautiful web-based YouTube downloader with real-time progress
"""

from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
import threading
from pathlib import Path
import uuid

app = Flask(__name__)

# Store active downloads and their progress
downloads = {}


class DownloadProgress:
    """Track download progress for real-time updates"""
    def __init__(self, download_id):
        self.download_id = download_id
        self.status = "starting"
        self.progress = 0
        self.speed = 0
        self.eta = 0
        self.title = ""
        self.error = None
        self.file_path = None

    def update(self, d):
        """Progress hook callback from yt-dlp"""
        if d['status'] == 'downloading':
            # Calculate progress percentage
            # Handle cases where total_bytes might be None (livestreams, some videos)
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded_bytes = d.get('downloaded_bytes', 0)

            if total_bytes and total_bytes > 0:
                self.progress = (downloaded_bytes / total_bytes) * 100
            else:
                # If no total size, just show that we're downloading
                self.progress = 50  # Indeterminate progress

            self.speed = d.get('speed', 0) / 1_000_000 if d.get('speed') else 0  # Convert to MB/s
            self.eta = d.get('eta', 0)
            self.status = "downloading"

        elif d['status'] == 'finished':
            self.progress = 100
            self.status = "processing"
            self.file_path = d['filename']


def download_video(download_id, url, quality, save_path):
    """
    Download video in background thread
    Updates progress object in real-time
    """
    progress = downloads[download_id]

    try:
        # Map quality to yt-dlp format
        quality_map = {
            "2160p (4K)": "bestvideo[height<=2160]+bestaudio/best[height<=2160]",
            "1440p (2K)": "bestvideo[height<=1440]+bestaudio/best[height<=1440]",
            "1080p (Full HD)": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "720p (HD)": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "Best Available": "bestvideo+bestaudio/best"
        }

        format_selector = quality_map.get(quality, "bestvideo+bestaudio/best")

        # Configure yt-dlp options
        ydl_opts = {
            'format': format_selector,
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
            'progress_hooks': [progress.update],
            'merge_output_format': 'mp4',
            'postprocessor_args': ['-c:v', 'copy', '-c:a', 'aac'],
            'quiet': False,  # Show errors
            'no_warnings': False,  # Show warnings
            'socket_timeout': 30,  # Timeout for network operations
            'retries': 3,  # Retry failed downloads
            'fragment_retries': 3,  # Retry failed fragments
            'http_chunk_size': 10485760,  # 10MB chunks (helps with broken pipe)
        }

        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            progress.title = info.get('title', 'video')
            progress.status = "completed"
            progress.progress = 100

    except Exception as e:
        # Handle any errors
        progress.status = "error"
        progress.error = str(e)


@app.route('/')
def index():
    """Serve the main web app"""
    return render_template('index.html')


@app.route('/api/download', methods=['POST'])
def start_download():
    """
    API endpoint to start a download
    Returns download_id for tracking progress
    """
    data = request.json
    url = data.get('url')
    quality = data.get('quality', '2160p (4K)')
    save_path = data.get('save_path', str(Path.home() / "Downloads"))

    # Validate URL
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    # Create unique download ID
    download_id = str(uuid.uuid4())

    # Create progress tracker
    progress = DownloadProgress(download_id)
    downloads[download_id] = progress

    # Start download in background thread
    thread = threading.Thread(
        target=download_video,
        args=(download_id, url, quality, save_path),
        daemon=True
    )
    thread.start()

    return jsonify({'download_id': download_id})


@app.route('/api/progress/<download_id>')
def get_progress(download_id):
    """
    API endpoint to check download progress
    Returns real-time status, progress percentage, speed, etc.
    """
    progress = downloads.get(download_id)

    if not progress:
        return jsonify({'error': 'Download not found'}), 404

    return jsonify({
        'status': progress.status,
        'progress': progress.progress,
        'speed': progress.speed,
        'eta': progress.eta,
        'title': progress.title,
        'error': progress.error
    })


if __name__ == '__main__':
    # Run Flask development server
    # For production, use gunicorn or waitress
    app.run(debug=True, host='0.0.0.0', port=5001)
