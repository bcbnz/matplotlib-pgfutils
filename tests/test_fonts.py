from .utils import build_figure, clean_dir
import os.path

base = os.path.normpath(os.path.dirname(__file__))


def test_custom_font():
    """Test figure using a custom font with fontspec in config file..."""
    dir = os.path.join(base, "sources", "fonts")
    res = build_figure(dir, "custom_font.py")
    assert res.returncode == 0, "Failed to build tests/sources/fonts/custom_font.py"
    clean_dir(dir)


def test_custom_font_kwargs():
    """Test figure using a custom font specified through kwargs..."""
    dir = os.path.join(base, "sources", "fonts", "noconfig")
    res = build_figure(dir, "custom_font.py")
    assert res.returncode == 0, "Failed to build tests/sources/fonts/no_config/custom_font.py"
    clean_dir(dir)
