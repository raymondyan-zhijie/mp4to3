"""Foundation dataclasses and types used by all core modules."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

APP_NAME = "MP4to3"


class ConversionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AppPaths:
    """Centralized cross-platform path management via platformdirs."""

    data_dir: Path
    config_toml: Path
    history_db: Path
    config_json: Path
    history_json: Path
    log_file: Path

    @classmethod
    def create(cls) -> AppPaths:
        from platformdirs import PlatformDirs

        pd = PlatformDirs(APP_NAME, appauthor=False, roaming=True)
        data_dir = Path(pd.user_data_path)
        data_dir.mkdir(parents=True, exist_ok=True)
        return cls(
            data_dir=data_dir,
            config_toml=data_dir / "config.toml",
            history_db=data_dir / "history.db",
            config_json=data_dir / "config.json",
            history_json=data_dir / "conversion_history.json",
            log_file=data_dir / "converter.log",
        )


@dataclass
class ConversionConfig:
    """Persisted user preferences. Fields use TOML-compatible types."""

    bitrate: str = "192k"
    output_dir: str = ""  # resolved to default at load time
    sample_rate: int = 44100


@dataclass
class ConversionTask:
    """A single file conversion unit. Status mutated by the engine."""

    source_path: Path
    output_path: Path
    bitrate: str = "192k"
    sample_rate: int = 44100
    status: ConversionStatus = ConversionStatus.PENDING
    error_message: Optional[str] = None
    duration: Optional[float] = None


@dataclass
class HistoryRecord:
    """One row in the history database."""

    id: int = -1
    timestamp: str = ""
    source_name: str = ""
    output_name: str = ""
    source_path: str = ""
    output_path: str = ""
    bitrate: str = "192k"
    duration: float = 0.0
    status: str = "completed"
