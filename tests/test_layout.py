from pathlib import Path

from lib.layout import ProjectLayout


def test_project_layout_paths():
    layout = ProjectLayout(Path("project"))

    assert layout.input == Path("project/input")
    assert layout.md == Path("project/md")
    assert layout.analysis == Path("project/analysis")
    assert layout.mmpbsa == Path("project/mmpbsa")

    assert layout.trajectory == Path("project/analysis/trajectory")
    assert layout.rmsd == Path("project/analysis/rmsd")
    assert layout.rmsf == Path("project/analysis/rmsf")
    assert layout.rg == Path("project/analysis/rg")
    assert layout.sasa == Path("project/analysis/sasa")
    assert layout.hbond == Path("project/analysis/hbond")
    assert layout.com == Path("project/analysis/com")
    assert layout.system == Path("project/analysis/system")


def test_create_layout(tmp_path):
    layout = ProjectLayout(tmp_path)

    layout.create()

    assert layout.input.exists()
    assert layout.md.exists()
    assert layout.analysis.exists()
    assert layout.trajectory.exists()
    assert layout.rmsd.exists()
    assert layout.rmsf.exists()
    assert layout.rg.exists()
    assert layout.sasa.exists()
    assert layout.hbond.exists()
    assert layout.com.exists()
    assert layout.system.exists()
    assert layout.mmpbsa.exists()
