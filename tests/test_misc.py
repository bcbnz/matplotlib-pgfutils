# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

import os
from pathlib import Path

import pytest

from pgfutils import save, setup_figure

from .utils import build_pypgf

srcdir = Path(__file__).parent.parent


class TestMiscClass:
    def test_save_with_figure(self):
        """Test save() works when given an explicit figure instance..."""
        setup_figure(width=1, height=1)
        from matplotlib import pyplot as plt

        fig = plt.figure()
        save(fig)
        os.unlink("tests/test_misc.pypgf")

    def test_save_with_nonfigure_fails(self):
        """Test save() fails when given a non-figure object..."""
        setup_figure(width=1, height=1)
        with pytest.raises(AttributeError):
            save(self)

    def test_readme_example(self, tmpdir):
        """Check example in README can be built..."""
        # Figure out some paths.
        rfn = srcdir / "README.md"
        sfn = tmpdir / "readme.py"

        # Extract the example from the README.
        with open(rfn, "r") as readme, open(sfn, "w") as script:
            in_script = False
            for line in readme:
                sline = line.rstrip()
                if in_script:
                    if sline == "```":
                        break
                    script.write(line)
                else:
                    if sline == "```python":
                        in_script = True

        # Confirm it builds.
        with build_pypgf(tmpdir, "readme.py") as res:
            assert res.returncode == 0, "Could not build README example."
