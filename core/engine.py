"""FFmpeg-based video-to-MP3 converter using direct subprocess calls."""

from __future__ import annotations

import logging
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable, Optional

from imageio_ffmpeg import get_ffmpeg_exe

from core.models import ConversionStatus, ConversionTask

SUPPORTED_EXTENSIONS: frozenset[str] = frozenset({
    ".mp4", ".avi", ".mkv", ".mov", ".flv", ".wmv",
    ".m4v", ".webm", ".ts", ".mts",
})


def resolve_output_path(output_dir: Path, source_name: str) -> Path:
    """Build output .mp3 path, avoiding name collisions.

    Given "video.mp4" produces output_dir / "video.mp3".
    If that exists, tries "video_1.mp3", "video_2.mp3", etc.
    """
    stem = Path(source_name).stem
    candidate = output_dir / f"{stem}.mp3"
    counter = 1
    while candidate.exists():
        candidate = output_dir / f"{stem}_{counter}.mp3"
        counter += 1
    return candidate


def _get_ffprobe_path() -> Optional[Path]:
    """Resolve ffprobe next to the bundled ffmpeg binary.

    Returns ``None`` when ffprobe is not available (``imageio-ffmpeg``
    bundles only ffmpeg, not ffprobe).
    """
    ffmpeg = Path(get_ffmpeg_exe())
    suffix = ".exe" if sys.platform == "win32" else ""
    ffprobe = ffmpeg.with_name(f"ffprobe{suffix}")
    if not ffprobe.exists():
        logging.info(
            "ffprobe 不可用 (imageio-ffmpeg 仅包含 ffmpeg)，将跳过音频轨道检测"
        )
        return None
    return ffprobe


class FFMpegConverter:
    """Convert video files to MP3 by shelling out to bundled ffmpeg.

    Supports:
    - ``-acodec copy`` fast path when source audio is already MP3
    - Real-time progress via stderr ``time=`` parsing
    """

    def __init__(self, ffmpeg_path: Optional[str] = None) -> None:
        self._ffmpeg_path: str = ffmpeg_path or get_ffmpeg_exe()
        self._cancel: bool = False
        self._process: Optional[subprocess.Popen] = None

    @property
    def is_cancelled(self) -> bool:
        return self._cancel

    def cancel(self) -> None:
        """Set cancel flag and terminate running subprocess."""
        self._cancel = True
        if self._process is not None and self._process.poll() is None:
            self._process.terminate()

    def reset_cancel(self) -> None:
        """Reset cancel state before a new batch."""
        self._cancel = False
        self._process = None

    def convert_file(
        self,
        source: Path,
        output: Path,
        bitrate: str = "192k",
        sample_rate: int = 44100,
        on_progress: Optional[Callable[[float], None]] = None,
    ) -> None:
        """Convert one video file to MP3. Blocks until done or cancelled.

        Raises:
            FileNotFoundError: source does not exist.
            ValueError: zero-byte file or no audio track.
            RuntimeError: ffmpeg returned non-zero exit code.
        """
        if not source.exists():
            raise FileNotFoundError(f"源文件不存在: {source}")
        if source.stat().st_size == 0:
            raise ValueError(f"源文件大小为 0 字节: {source}")

        # Probe source for audio codec and duration
        audio_codec, total_duration = self._probe_source(source)

        if not audio_codec and not self._source_has_audio(source):
            raise ValueError(f"视频文件没有音频轨道: {source.name}")

        output.parent.mkdir(parents=True, exist_ok=True)

        use_copy = audio_codec and audio_codec.lower() == "mp3"

        cmd = [
            self._ffmpeg_path,
            "-y",
            "-i", str(source),
            "-vn",
        ]
        if use_copy:
            cmd.extend(["-acodec", "copy"])
            logging.info(f"检测到 MP3 音频，使用无损复制: {source.name}")
        else:
            cmd.extend([
                "-c:a", "libmp3lame",
                "-b:a", bitrate,
                "-ar", str(sample_rate),
            ])
        cmd.append(str(output))

        stderr_lines: list[str] = []
        try:
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            last_pct = -1
            for line in self._process.stderr:
                stderr_lines.append(line)
                if self._cancel:
                    self._process.terminate()
                    break
                if on_progress and total_duration > 0:
                    m = re.search(
                        r"time=(\d+):(\d+):(\d+)\.(\d+)", line
                    )
                    if m:
                        current = (
                            int(m.group(1)) * 3600
                            + int(m.group(2)) * 60
                            + int(m.group(3))
                            + int(m.group(4)) / 100.0
                        )
                        pct = min(int(current / total_duration * 100), 99)
                        if pct > last_pct:
                            last_pct = pct
                            on_progress(pct)

            if on_progress and not self._cancel:
                on_progress(100)

            returncode = self._process.wait()
        finally:
            self._process = None

        if self._cancel:
            return

        if returncode != 0:
            stderr_str = "".join(stderr_lines)
            error_tail = (
                stderr_str.strip().split("\n")[-3:]
                if stderr_str.strip()
                else ["未知错误"]
            )
            raise RuntimeError("\n".join(error_tail))

    def convert_batch(
        self,
        tasks: list[ConversionTask],
        on_progress: Optional[Callable[[int, int, str], None]] = None,
        on_task_done: Optional[Callable[[ConversionTask], None]] = None,
        on_file_progress: Optional[Callable[[float], None]] = None,
    ) -> list[ConversionTask]:
        """Convert all tasks sequentially. Mutates task objects in-place.

        *on_progress* receives ``(done, total, filename)`` for batch-level
        status. *on_file_progress* receives ``(pct)`` (0–100) for per-file
        progress, driven by ffmpeg ``time=`` stderr output.
        """
        self.reset_cancel()
        total = len(tasks)

        for i, task in enumerate(tasks):
            if self._cancel:
                task.status = ConversionStatus.CANCELLED
                task.error_message = "用户取消"
                continue

            if on_progress:
                on_progress(i + 1, total, task.source_path.name)

            task.status = ConversionStatus.RUNNING
            start = time.time()

            try:
                self.convert_file(
                    task.source_path,
                    task.output_path,
                    task.bitrate,
                    task.sample_rate,
                    on_progress=on_file_progress,
                )
                if self._cancel:
                    task.status = ConversionStatus.CANCELLED
                    task.error_message = "用户取消"
                else:
                    task.status = ConversionStatus.COMPLETED
            except Exception as e:
                task.status = ConversionStatus.FAILED
                task.error_message = str(e)
                logging.error(f"转换失败: {task.source_path.name} - {e}")
            finally:
                task.duration = time.time() - start

            if on_task_done:
                on_task_done(task)

        return tasks

    # ------------------------------------------------------------------
    # Source probing
    # ------------------------------------------------------------------

    def _probe_source(self, source: Path) -> tuple[str, float]:
        """Run ``ffmpeg -i`` to extract audio codec and duration.

        Returns ``(codec_name, duration_seconds)``. Both are empty/zero
        when detection fails.
        """
        cmd = [self._ffmpeg_path, "-i", str(source)]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                encoding="utf-8",
                errors="replace",
            )
            stderr = result.stderr
            codec = self._parse_audio_codec(stderr)
            duration = self._parse_duration(stderr)
            return codec, duration
        except Exception:
            return "", 0.0

    @staticmethod
    def _parse_audio_codec(stderr: str) -> str:
        """Extract audio codec name from ffmpeg stderr."""
        m = re.search(r"Audio:\s*(\w+)", stderr)
        return m.group(1) if m else ""

    @staticmethod
    def _parse_duration(stderr: str) -> float:
        """Extract Duration from ffmpeg stderr, return seconds."""
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+)\.(\d+)", stderr)
        if m:
            return (
                int(m.group(1)) * 3600
                + int(m.group(2)) * 60
                + int(m.group(3))
                + int(m.group(4)) / 100.0
            )
        return 0.0

    def _source_has_audio(self, source: Path) -> bool:
        """Check if the source file contains an audio stream via ffprobe.

        When ffprobe is unavailable, conservatively assumes audio is present
        so conversion proceeds (ffmpeg will report the actual error).
        """
        ffprobe_path = _get_ffprobe_path()
        if ffprobe_path is None:
            return True
        try:
            result = subprocess.run(
                [str(ffprobe_path), "-v", "error", "-show_entries",
                 "stream=codec_type", "-of", "csv=p=0", str(source)],
                capture_output=True, text=True, timeout=30,
                encoding="utf-8", errors="replace",
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return True
        return "audio" in result.stdout
