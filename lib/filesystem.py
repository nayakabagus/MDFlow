"""
MDFlow Filesystem Module

Common filesystem utilities used throughout MDFlow.
"""

from __future__ import annotations

import shutil
from pathlib import Path


class FileSystem:
    """Filesystem helper class."""

    @staticmethod
    def ensure_dir(path: str | Path) -> Path:
        """Create directory if it does not exist."""
        directory = Path(path)
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    @staticmethod
    def exists(path: str | Path) -> bool:
        """Check whether a file or directory exists."""
        return Path(path).exists()

    @staticmethod
    def remove(path: str | Path) -> None:
        """Remove file or directory."""
        target = Path(path)

        if not target.exists():
            return

        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()

    @staticmethod
    def copy(src: str | Path, dst: str | Path) -> None:
        """Copy file."""
        shutil.copy2(src, dst)

    @staticmethod
    def copy_tree(src: str | Path, dst: str | Path) -> None:
        """Copy an entire directory tree."""
        shutil.copytree(src, dst, dirs_exist_ok=True)

    @staticmethod
    def move(src: str | Path, dst: str | Path) -> None:
        """Move file."""
        shutil.move(src, dst)
