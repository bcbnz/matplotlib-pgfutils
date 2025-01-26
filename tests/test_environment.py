# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from pathlib import Path

from .utils import build_pypgf


srcdir = Path(__file__).parent.resolve() / "sources" / "environment"


def test_environment_set():
    """Check environment variables can be set..."""
    with build_pypgf(srcdir / "check_set", "basic.py") as res:
        assert res.returncode == 0, "Environment variables not set correctly."


def test_environment_override():
    """Check environment variables can override existing ones..."""
    with build_pypgf(srcdir / "check_set", "override.py") as res:
        assert res.returncode == 0, "Environment variables not set correctly."


def test_environment_repeated():
    """Check the last value of repeated environment variables is used..."""
    with build_pypgf(srcdir / "repeated", "basic.py") as res:
        assert res.returncode == 0, "Environment variables not set correctly."


def test_environment_invalid():
    """Check invalid environment variable in configuration is rejected..."""
    with build_pypgf(srcdir / "invalid", "basic.py") as res:
        assert res.returncode != 0, "Configuration not rejected."
        assert (
            "Environment variables should be in the form" in res.stderr
        ), "Incorrect message."
