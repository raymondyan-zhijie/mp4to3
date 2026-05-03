"""PyInstaller runtime hook: set IMAGEIO_FFMPEG_EXE for bundled ffmpeg.

imageio-ffmpeg's ``get_ffmpeg_exe()`` checks this env var first, which
avoids importlib.resources resolution issues inside a PyInstaller bundle.
"""

import os
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    meipass = Path(sys._MEIPASS)
    for candidate in meipass.glob("**/ffmpeg*"):
        name = candidate.name
        if name.startswith("ffmpeg") and not name.startswith("ffprobe"):
            os.environ["IMAGEIO_FFMPEG_EXE"] = str(candidate)
            break
