"""
MDFlow Resource Manager

Utilities for accessing built-in resources distributed with MDFlow.
"""

from __future__ import annotations

from pathlib import Path

from lib.filesystem import FileSystem
from lib.layout import ProjectLayout


class ResourceManager:
    """Access bundled MDFlow resources."""

    @staticmethod
    def project_root() -> Path:
        """
        Return the MDFlow project root directory.
        """
        return Path(__file__).resolve().parent.parent

    @staticmethod
    def templates_dir() -> Path:
        """
        Return the templates directory.
        """
        return ResourceManager.project_root() / "templates"

    @staticmethod
    def forcefield_dir(forcefield: str = "amber99sb-ildn") -> Path:
        """
        Return the template directory for a force field.
        """
        return ResourceManager.templates_dir() / forcefield

    @staticmethod
    def install_templates(
        layout: ProjectLayout,
        forcefield: str = "amber99sb-ildn",
    ) -> None:
        """
        Copy bundled MDP templates into the project.
        """
        FileSystem.copy_tree(
            ResourceManager.forcefield_dir(forcefield),
            layout.md,
        )
