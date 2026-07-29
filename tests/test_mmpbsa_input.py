from pathlib import Path

from lib.mmpbsa_input import MMPBSAInput


def test_render_contains_general_block() -> None:
    config = MMPBSAInput()

    text = config.render()

    assert "&general" in text
    assert "startframe=1" in text
    assert "interval=1" in text


def test_write(tmp_path: Path) -> None:
    output = tmp_path / "mmpbsa.in"

    config = MMPBSAInput()

    config.write(output)

    assert output.exists()
    assert "&general" in output.read_text(encoding="utf-8")
