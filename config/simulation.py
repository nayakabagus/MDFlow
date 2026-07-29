"""
Simulation configuration for MDFlow.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class SimulationConfig:
    """
    Configuration for a molecular dynamics simulation.
    """

    # Force field
    forcefield: str = "amber99sb-ildn"

    # Water model
    water_model: str = "tip3p"

    # Box settings
    box_type: str = "dodecahedron"
    box_distance: float = 1.0

    # Ion names
    positive_ion: str = "NA"
    negative_ion: str = "CL"

    # File locations
    template_dir: Path = Path("templates")

    @property
    def em_mdp(self) -> Path:
        return self.template_dir / "em.mdp"

    @property
    def ions_mdp(self) -> Path:
        return self.template_dir / "ions.mdp"

    @property
    def nvt_mdp(self) -> Path:
        return self.template_dir / "nvt.mdp"

    @property
    def npt_mdp(self) -> Path:
        return self.template_dir / "npt.mdp"

    @property
    def md_mdp(self) -> Path:
        return self.template_dir / "md.mdp"
