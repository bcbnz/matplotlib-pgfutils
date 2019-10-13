import os.path
from .utils import build_figure, clean_dir
import pytest

srcdir = os.path.join(os.path.normpath(os.path.dirname(__file__)), "sources", "external")


def test_cartopy():
    """Check a cartopy figure can be generated..."""
    try:
        import cartopy
    except ImportError:
        pytest.skip("cartopy not available for testing")

    res = build_figure(srcdir, "cartopy_figure.py")
    assert res.returncode == 0, "tests/sources/external/cartopy_figure.py could not be built."
    clean_dir(srcdir)


def test_seaborn():
    """Check a seaborn figure can be generated..."""
    try:
        import seaborn
    except ImportError:
        pytest.skip("seaborn not available for testing")

    res = build_figure(srcdir, "seaborn_figure.py")
    assert res.returncode == 0, "tests/sources/external/seaborn_figure.py could not be built."
    clean_dir(srcdir)

