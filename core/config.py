"""TOML-based configuration management with legacy JSON migration."""

from __future__ import annotations

import json
import logging
import os
import tomllib
import tomli_w
from pathlib import Path
from typing import Optional

from core.models import AppPaths, ConversionConfig


class ConfigManager:
    """Load and persist ConversionConfig as TOML. One-time migration from JSON."""

    def __init__(self, paths: AppPaths) -> None:
        self._paths = paths
        self._config: Optional[ConversionConfig] = None

    def load(self) -> ConversionConfig:
        """Load config from TOML, falling back to JSON migration, then defaults."""
        if self._paths.config_toml.exists():
            config = self._load_toml()
            if config:
                self._config = config
                logging.info("配置从 TOML 加载成功")
                return self._config

        config = self._migrate_from_json()
        if config:
            self._config = config
            logging.info("配置从 JSON 迁移成功")
            return self._config

        self._config = ConversionConfig(
            bitrate="192k",
            output_dir=str(Path.home() / "Music"),
            sample_rate=44100,
        )
        self.save(self._config)
        logging.info("使用默认配置")
        return self._config

    def save(self, config: ConversionConfig) -> None:
        """Persist config to TOML atomically."""
        tmp_path = self._paths.config_toml.with_suffix(".tmp")
        data = {
            "bitrate": config.bitrate,
            "output_dir": config.output_dir,
            "sample_rate": config.sample_rate,
        }
        try:
            with open(tmp_path, "wb") as f:
                tomli_w.dump(data, f)
            os.replace(str(tmp_path), str(self._paths.config_toml))
            logging.info("配置保存成功")
        except Exception as e:
            logging.error(f"配置保存失败: {e}")
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)

    @property
    def config(self) -> ConversionConfig:
        if self._config is None:
            raise RuntimeError("ConfigManager.load() must be called before accessing .config")
        return self._config

    def _load_toml(self) -> Optional[ConversionConfig]:
        try:
            with open(self._paths.config_toml, "rb") as f:
                data = tomllib.load(f)
            return ConversionConfig(
                bitrate=data.get("bitrate", "192k"),
                output_dir=data.get("output_dir", str(Path.home() / "Music")),
                sample_rate=data.get("sample_rate", 44100),
            )
        except Exception as e:
            logging.error(f"TOML 加载失败: {e}")
            return None

    def _migrate_from_json(self) -> Optional[ConversionConfig]:
        json_path = self._paths.config_json
        if not json_path.exists():
            return None
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                legacy = json.load(f)
            config = ConversionConfig(
                bitrate=legacy.get("bitrate", "192k"),
                output_dir=legacy.get("output_dir", str(Path.home() / "Music")),
                sample_rate=44100,
            )
            self.save(config)
            bak_path = json_path.with_suffix(".json.bak")
            os.replace(str(json_path), str(bak_path))
            logging.info("JSON 配置已迁移至 TOML")
            return config
        except Exception as e:
            logging.error(f"JSON 迁移失败: {e}")
            return None
