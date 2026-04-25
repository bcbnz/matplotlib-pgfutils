# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from pathlib import Path

from .utils import build_pypgf, build_tex

srcdir = Path(__file__).parent / "sources"


def test_fix_raster_paths():
    """Check fix_raster_paths works..."""
    dir = srcdir / "fix_raster_paths"

    with build_pypgf(dir, "figures/noise.py") as res:
        assert res.returncode == 0, f"Building {dir / 'figures/noise.py'} failed."

    with build_pypgf(dir, "speckle.py") as res:
        assert res.returncode == 0, f"Building {dir / 'speckle.pypgf'} failed."

        with build_tex(dir, "document") as tex_res:
            assert tex_res.returncode == 0, (
                "Building tests/sources/fix_raster_paths/document.pdf failed."
            )


def test_tracking_fix_raster_paths():
    """Check file tracking works with fix_raster_paths..."""
    dir = srcdir / "fix_raster_paths"

    with build_pypgf(dir, "figures/noise.py", {"PGFUTILS_TRACK_FILES": "1"}) as res:
        assert res.returncode == 0, f"Building {dir / 'figures/noise.py'} failed."
        expected = {
            "r:pgfutils.toml",
            "w:figures/noise-img0.png",
            "w:figures/noise-img1.png",
        }
        actual = set(res.stdout.strip().splitlines())
        assert actual == expected, "Tracked file mismatch."

    with build_pypgf(dir, "speckle.py", {"PGFUTILS_TRACK_FILES": "1"}) as res:
        assert res.returncode == 0, f"Building {dir / 'speckle.pypgf'} failed."
        expected = {
            "r:pgfutils.toml",
            "w:speckle-img0.png",
            "w:speckle-img1.png",
        }
        actual = set(res.stdout.strip().splitlines())
        assert actual == expected, "Tracked file mismatch."


def test_tikzpicture():
    """Check tikzpicture postprocessing works..."""
    dir = srcdir / "tikzpicture"
    with build_pypgf(dir, "square.py") as res:
        assert res.returncode == 0, f"Building {dir / 'square.pypgf'} failed."

        with build_tex(dir, "document_pgf") as tex_res:
            assert tex_res.returncode != 0, (
                "Document should have failed to built without the tikz package."
            )

        with build_tex(dir, "document_tikz") as tex_res:
            assert tex_res.returncode == 0, (
                "Document failed to build with the tikz package."
            )
