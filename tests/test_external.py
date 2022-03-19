import os.path

import pytest

from .utils import build_figure, clean_dir


srcdir = os.path.join(
    os.path.normpath(os.path.dirname(__file__)), "sources", "external"
)


def test_cartopy():
    """Check a cartopy figure can be generated..."""
    pytest.importorskip("cartopy", reason="artopy not available for testing")

    res = build_figure(srcdir, "cartopy_figure.py")
    assert (
        res.returncode == 0
    ), "tests/sources/external/cartopy_figure.py could not be built."
    clean_dir(srcdir)


def test_seaborn():
    """Check a seaborn figure can be generated..."""
    pytest.importorskip("seaborn", reason="seaborn not available for testing")

    res = build_figure(srcdir, "seaborn_figure.py")
    if res.returncode != 0:
        # Due to an upstream Matplotlib bug.
        if "'NoneType' object has no attribute 'write'" in res.stderr:
            pytest.xfail("https://github.com/mwaskom/seaborn/issues/2343")
    assert (
        res.returncode == 0
    ), "tests/sources/external/seaborn_figure.py could not be built."
    clean_dir(srcdir)
