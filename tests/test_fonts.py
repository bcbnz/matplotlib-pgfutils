from pathlib import Path

from .utils import build_pypgf


srcdir = Path(__file__).parent.resolve() / "sources" / "fonts"


def test_custom_font():
    """Test figure using a custom font with fontspec in config file..."""
    with build_pypgf(srcdir, "custom_font.py") as res:
        assert res.returncode == 0, "Failed to build tests/sources/fonts/custom_font.py"


def test_custom_font_kwargs():
    """Test figure using a custom font specified through kwargs..."""
    with build_pypgf(srcdir / "noconfig", "custom_font.py") as res:
        assert (
            res.returncode == 0
        ), "Failed to build tests/sources/fonts/no_config/custom_font.py"
