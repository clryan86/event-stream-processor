from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Settings:
    database_path: Path
    max_attempts: int = 3
    app_name: str = "Event Stream Processor"

    @classmethod
    def from_env(cls):
        root = Path(__file__).resolve().parents[1]
        return cls(Path(os.getenv("DATABASE_PATH", root / "data" / "events.db")), int(os.getenv("MAX_ATTEMPTS", "3")))
