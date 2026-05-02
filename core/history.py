"""SQLite-backed conversion history with legacy JSON migration."""

from __future__ import annotations

import json
import logging
import os
import sqlite3
from pathlib import Path
from typing import Optional

from core.models import AppPaths, HistoryRecord

_SCHEMA = """
CREATE TABLE IF NOT EXISTS history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   TEXT    NOT NULL,
    source_name TEXT    NOT NULL,
    output_name TEXT    NOT NULL,
    source_path TEXT    NOT NULL,
    output_path TEXT    NOT NULL,
    bitrate     TEXT    NOT NULL,
    duration    REAL    NOT NULL,
    status      TEXT    NOT NULL
);
"""


class HistoryStore:
    """SQLite-backed conversion history with WAL mode and JSON migration."""

    def __init__(self, paths: AppPaths) -> None:
        self._conn = sqlite3.connect(
            str(paths.history_db),
            check_same_thread=False,
        )
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=OFF")
        self._init_schema()
        migrated = self._migrate_from_json(paths.history_json)
        if migrated > 0:
            logging.info(f"从 JSON 迁移了 {migrated} 条历史记录")

    def _init_schema(self) -> None:
        self._conn.execute(_SCHEMA)
        self._conn.commit()

    def add(self, record: HistoryRecord) -> int:
        """Insert a record. Returns the new row ID."""
        cursor = self._conn.execute(
            """INSERT INTO history
               (timestamp, source_name, output_name, source_path,
                output_path, bitrate, duration, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                record.timestamp,
                record.source_name,
                record.output_name,
                record.source_path,
                record.output_path,
                record.bitrate,
                record.duration,
                record.status,
            ),
        )
        self._conn.commit()
        return cursor.lastrowid

    def get_all(self, limit: int = 100, offset: int = 0) -> list[HistoryRecord]:
        """Return recent records, newest first."""
        rows = self._conn.execute(
            "SELECT * FROM history ORDER BY id DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
        return [self._row_to_record(row) for row in rows]

    def count(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) as cnt FROM history").fetchone()
        return row["cnt"]

    def clear(self) -> None:
        self._conn.execute("DELETE FROM history")
        self._conn.execute("VACUUM")
        self._conn.commit()
        logging.info("历史记录已清空")

    def close(self) -> None:
        self._conn.close()

    def _migrate_from_json(self, json_path: Path) -> int:
        """One-time migration from legacy JSON. Returns count of migrated records."""
        if not json_path.exists():
            return 0
        if self.count() > 0:
            return 0
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                legacy = json.load(f)
            if not isinstance(legacy, list):
                return 0
            count = 0
            for item in legacy:
                self.add(
                    HistoryRecord(
                        timestamp=item.get("time", ""),
                        source_name=Path(item.get("source", "")).name,
                        output_name=Path(item.get("output", "")).name,
                        source_path=item.get("source", ""),
                        output_path=item.get("output", ""),
                        bitrate=item.get("bitrate", "192k"),
                        duration=self._parse_duration(item.get("duration", "0")),
                        status="completed",
                    )
                )
                count += 1
            bak_path = json_path.with_suffix(".json.bak")
            os.replace(str(json_path), str(bak_path))
            logging.info(f"历史记录从 JSON 迁移完成: {count} 条")
            return count
        except Exception as e:
            logging.error(f"历史记录 JSON 迁移失败: {e}")
            return 0

    @staticmethod
    def _parse_duration(value: str) -> float:
        """Parse a timedelta string like '0:01:23' into seconds."""
        try:
            parts = value.split(":")
            if len(parts) == 3:
                h, m, s = parts
                return int(h) * 3600 + int(m) * 60 + int(s)
            return 0.0
        except (ValueError, AttributeError):
            return 0.0

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> HistoryRecord:
        return HistoryRecord(
            id=row["id"],
            timestamp=row["timestamp"],
            source_name=row["source_name"],
            output_name=row["output_name"],
            source_path=row["source_path"],
            output_path=row["output_path"],
            bitrate=row["bitrate"],
            duration=row["duration"],
            status=row["status"],
        )
