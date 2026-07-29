"""
MDFlow Logger Module

Provides a lightweight logging system for MDFlow.
All modules should use this logger instead of print().
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


class Logger:
    """Simple logger for console and log file."""

    def __init__(self, log_dir: str = "logs") -> None:
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"mdflow_{timestamp}.log"

    def _log(self, level: str, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] [{level}] {message}"

        print(line)

        with self.log_file.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def info(self, message: str) -> None:
        self._log("INFO", message)

    def success(self, message: str) -> None:
        self._log("SUCCESS", message)

    def warning(self, message: str) -> None:
        self._log("WARNING", message)

    def error(self, message: str) -> None:
        self._log("ERROR", message)


# Global logger instance
logger = Logger()
