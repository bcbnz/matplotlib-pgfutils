import os.path
from .utils import build_figure, clean_dir

base = os.path.normpath(os.path.dirname(__file__))

try:
    import cartopy
except ImportError:
    cartopy = None

try:
    import seaborn
except ImportError:
    seaborn = None


if cartopy:
    def test_cartopy():
        """Check a cartopy figure can be generated..."""
        dir = os.path.join(base, "sources", "external")
        res = build_figure(dir, "cartopy_figure.py")
        assert res.returncode == 0, "tests/sources/external/cartopy_figure.py could not be built."
        clean_dir(dir)


if seaborn:
    def test_seaborn():
        """Check a seaborn figure can be generated..."""
        dir = os.path.join(base, "sources", "external")
        res = build_figure(dir, "seaborn_figure.py")
        assert res.returncode == 0, "tests/sources/external/seaborn_figure.py could not be built."
        clean_dir(dir)

