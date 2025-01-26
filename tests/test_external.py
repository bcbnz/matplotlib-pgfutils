# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from pathlib import Path

import pytest

from .utils import build_pypgf

srcdir = Path(__file__).parent / "sources" / "external"


def test_cartopy():
    """Check a cartopy figure can be generated..."""
    pytest.importorskip("cartopy", reason="cartopy not available for testing")

    with build_pypgf(srcdir, "cartopy_figure.py") as res:
        assert res.returncode == 0, (
            f"{srcdir / 'cartopy_figure.py'} could not be built."
        )


def test_seaborn():
    """Check a seaborn figure can be generated..."""
    pytest.importorskip("seaborn", reason="seaborn not available for testing")

    with build_pypgf(srcdir, "seaborn_figure.py") as res:
        if res.returncode != 0:
            # Due to an upstream Matplotlib bug.
            if "'NoneType' object has no attribute 'write'" in res.stderr:
                pytest.xfail("https://github.com/mwaskom/seaborn/issues/2343")
        assert res.returncode == 0, (
            f"{srcdir / 'seaborn_figure.py'} could not be built."
        )
