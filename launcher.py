"""
Junay Downloader Launcher
This script starts the Flask server and opens the browser automatically
Used for packaging into a Windows .exe
"""

import sys
import os
import threading
import time
import webbrowser
from waitress import serve
from app import app

def open_browser():
    """Wait for server to start, then open browser with proper window size"""
    time.sleep(2)  # Wait for server to initialize

    # Try to open with specific size using browser-specific methods
    # Chrome/Edge on Windows: Use --window-size flag
    import subprocess
    import platform

    url = 'http://127.0.0.1:8080'

    # On Windows, try to launch Chrome/Edge with specific window size
    if platform.system() == 'Windows':
        # Try Chrome first
        chrome_paths = [
            r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            os.path.expanduser(r'~\AppData\Local\Google\Chrome\Application\chrome.exe'),
        ]

        # Try Edge if Chrome not found
        edge_paths = [
            r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
            r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
        ]

        launched = False

        # Try Chrome with window size (no app mode to allow scrolling and resizing)
        for chrome_path in chrome_paths:
            if os.path.exists(chrome_path):
                try:
                    subprocess.Popen([chrome_path, url, '--window-size=900,800', '--new-window'])
                    launched = True
                    break
                except:
                    pass

        # Try Edge if Chrome failed
        if not launched:
            for edge_path in edge_paths:
                if os.path.exists(edge_path):
                    try:
                        subprocess.Popen([edge_path, url, '--window-size=900,800', '--new-window'])
                        launched = True
                        break
                    except:
                        pass

        # Fall back to default browser
        if not launched:
            webbrowser.open(url)
    else:
        # For non-Windows, use default browser
        webbrowser.open(url)

def main():
    """Main entry point for the launcher"""
    print("=" * 60)
    print("  JUNAY 4K DOWNLOADER")
    print("  Starting server...")
    print("=" * 60)

    # Start browser in background thread
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    print("\nServer started!")
    print("Opening browser...")
    print("\nThe app is now running at: http://127.0.0.1:8080")
    print("\nPress CTRL+C to stop the server\n")

    # Start the production server (Waitress)
    # This is better than Flask's dev server for production use
    try:
        serve(app, host='127.0.0.1', port=8080, threads=4)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        sys.exit(0)

if __name__ == '__main__':
    main()
