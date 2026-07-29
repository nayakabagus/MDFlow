from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# TODO:
# - Support &gb section
# - Support &pb section
# - Support &decomposition section
# - Support &alanine_scanning section
# - Support &nmode section


@dataclass(slots=True)
class MMPBSAInput:
    """
    Generate a gmx_MMPBSA input file.
    """

    startframe: int = 1
    endframe: int | None = None
    interval: int = 1

    verbose: int = 1
    keep_files: int = 0

    def render(self) -> str:
        """
        Return the input file contents.
        """

        lines = [
            "&general",
            f"startframe={self.startframe},",
        ]

        if self.endframe is not None:
            lines.append(f"endframe={self.endframe},")

        lines.extend(
            [
                f"interval={self.interval},",
                f"verbose={self.verbose},",
                f"keep_files={self.keep_files},",
                "/",
                "",
            ]
        )

        return "\n".join(lines)

    def write(
        self,
        output: Path,
    ) -> Path:
        """
        Write the input file.
        """

        output.write_text(
            self.render(),
            encoding="utf-8",
        )

        return output
