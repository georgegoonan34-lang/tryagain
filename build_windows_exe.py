"""
Build script to package Junay Downloader as a Windows .exe
This creates a single executable file that Junay can run without any installation
"""

import PyInstaller.__main__
import os
import sys

def build_exe():
    """Build the Windows executable"""

    print("=" * 70)
    print("  BUILDING JUNAY DOWNLOADER FOR WINDOWS")
    print("=" * 70)
    print()

    # PyInstaller arguments for creating the exe
    # --name: Name of the output executable
    # --onefile: Bundle everything into a single .exe
    # --windowed: Don't show console window (clean GUI experience)
    # --add-data: Include the templates folder (Flask HTML files)
    # --hidden-import: Ensure waitress is included
    # --clean: Clean cache before building
    # --icon: Would add icon if we had one (.ico file)

    # Determine the separator for --add-data (different on Windows vs Mac/Linux)
    separator = ';' if sys.platform == 'win32' else ':'

    args = [
        'launcher.py',                              # Main script to run
        '--name=JunayDownloader',                   # Output name
        '--onefile',                                # Single file
        '--windowed',                               # No console window
        f'--add-data=templates{separator}templates', # Include HTML templates
        '--hidden-import=waitress',                 # Ensure waitress is bundled
        '--hidden-import=flask',                    # Ensure flask is bundled
        '--hidden-import=yt_dlp',                   # Ensure yt-dlp is bundled
        '--clean',                                  # Clean build
        '--noconfirm',                              # Overwrite without asking
    ]

    print("Configuration:")
    print(f"   - Main script: launcher.py")
    print(f"   - Output name: JunayDownloader.exe")
    print(f"   - Type: Single file executable")
    print(f"   - Mode: Windowed (no console)")
    print(f"   - Includes: Flask templates, all dependencies")
    print()
    print("Building... (this may take 2-5 minutes)")
    print()

    # Run PyInstaller
    PyInstaller.__main__.run(args)

    print()
    print("=" * 70)
    print("  BUILD COMPLETE!")
    print("=" * 70)
    print()
    print(f"Your executable is ready:")
    print(f"   Location: {os.path.join(os.getcwd(), 'dist', 'JunayDownloader.exe')}")
    print()
    print("Next steps:")
    print("   1. Go to the 'dist' folder")
    print("   2. Find 'JunayDownloader.exe'")
    print("   3. Send it to Junay via Google Drive, Dropbox, or WeTransfer")
    print("   4. Junay just needs to download and double-click it!")
    print()
    print("Tips:")
    print("   - File size will be ~60-80MB (includes Python + all dependencies)")
    print("   - Junay needs NO installation - just run the .exe")
    print("   - Windows might show SmartScreen warning (click 'More info' -> 'Run anyway')")
    print("   - The app will auto-open in his default browser")
    print()

if __name__ == "__main__":
    build_exe()
