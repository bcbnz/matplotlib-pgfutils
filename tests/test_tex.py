import os.path
from .utils import build_figure, build_tex

base = os.path.normpath(os.path.dirname(__file__))


class TestTexClass:
    def test_fix_raster_paths(self):
        """Check fix_raster_paths works..."""
        dir = os.path.join(base, "tex", "fix_raster_paths")
        res = build_figure(dir, "figures/noise.py")
        assert res.returncode == 0, "Building tests/tex/fix_raster_paths/figures/noise.pypgf failed."
        res = build_figure(dir, "speckle.py")
        assert res.returncode == 0, "Building tests/tex/fix_raster_paths/speckle.pypgf failed."
        res = build_tex(dir, "document")
        assert res.returncode == 0, "Building tests/tex/fix_raster_paths/document.pdf failed."


    def test_tikzpicture(self):
        """Check tikzpicture postprocessing works..."""
        dir = os.path.join(base, "tex", "tikzpicture")
        res = build_figure(dir, "square.py")
        assert res.returncode == 0, "Building tests/tex/tikzpicture/square.pypgf failed."
        res = build_tex(dir, "document_pgf")
        assert res.returncode != 0, "Document should have failed to built without the tikz package."
        res = build_tex(dir, "document_tikz")
        assert res.returncode == 0, "Document failed to build with the tikz package."
