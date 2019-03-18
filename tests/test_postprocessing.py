import os.path
from .utils import build_figure, build_tex, clean_dir

base = os.path.normpath(os.path.dirname(__file__))


class TestTexClass:
    def test_fix_raster_paths(self):
        """Check fix_raster_paths works..."""
        dir = os.path.join(base, "sources", "fix_raster_paths")
        res = build_figure(dir, "figures/noise.py")
        assert res.returncode == 0, "Building tests/tex/fix_raster_paths/figures/noise.pypgf failed."
        res = build_figure(dir, "speckle.py")
        assert res.returncode == 0, "Building tests/tex/fix_raster_paths/speckle.pypgf failed."
        res = build_tex(dir, "document")
        assert res.returncode == 0, "Building tests/tex/fix_raster_paths/document.pdf failed."
        clean_dir(dir)


    def test_tracking_fix_raster_paths(self):
        """Check file tracking works with fix_raster_paths..."""
        dir = os.path.join(base, "sources", "fix_raster_paths")
        res = build_figure(dir, "figures/noise.py", {"PGFUTILS_TRACK_FILES": "1"})
        assert res.returncode == 0, "Building tests/tex/fix_raster_paths/figures/noise.pypgf failed."
        expected = {
            'r:pgfutils.cfg',
            'w:figures/noise-img0.png',
            'w:figures/noise-img1.png',
        }
        actual = set(res.stdout.strip().splitlines())
        assert actual == expected, "Tracked file mismatch."

        res = build_figure(dir, "speckle.py", {"PGFUTILS_TRACK_FILES": "1"})
        assert res.returncode == 0, "Building tests/tex/fix_raster_paths/speckle.pypgf failed."
        expected = {
            'r:pgfutils.cfg',
            'w:speckle-img0.png',
            'w:speckle-img1.png',
        }
        actual = set(res.stdout.strip().splitlines())
        assert actual == expected, "Tracked file mismatch."
        clean_dir(dir)


    def test_tikzpicture(self):
        """Check tikzpicture postprocessing works..."""
        dir = os.path.join(base, "sources", "tikzpicture")
        res = build_figure(dir, "square.py")
        assert res.returncode == 0, "Building tests/tex/tikzpicture/square.pypgf failed."
        res = build_tex(dir, "document_pgf")
        assert res.returncode != 0, "Document should have failed to built without the tikz package."
        res = build_tex(dir, "document_tikz")
        assert res.returncode == 0, "Document failed to build with the tikz package."
        clean_dir(dir)
