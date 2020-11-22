import os.path
from .utils import build_figure, clean_dir
import pytest

srcdir = os.path.join(os.path.normpath(os.path.dirname(__file__)), "sources", "environment")


def test_environment_set():
    """Check environment variables can be set..."""
    res = build_figure(os.path.join(srcdir, "check_set"), "basic.py")
    assert res.returncode == 0, "Environment variables not set correctly."
    clean_dir(srcdir)


def test_environment_override():
    """Check environment variables can override existing ones..."""
    res = build_figure(os.path.join(srcdir, "check_set"), "override.py")
    assert res.returncode == 0, "Environment variables not set correctly."
    clean_dir(srcdir)


def test_environment_repeated():
    """Check the last value of repeated environment variables is used..."""
    res = build_figure(os.path.join(srcdir, "repeated"), "basic.py")
    assert res.returncode == 0, "Environment variables not set correctly."
    clean_dir(srcdir)


def test_environment_invalid():
    """Check invalid environment variable in configuration is rejected..."""
    res = build_figure(os.path.join(srcdir, "invalid"), "basic.py")
    assert res.returncode != 0, "Configuration not rejected."
    assert "Environment variables should be in the form" in res.stderr, "Incorrect message."
    clean_dir(srcdir)
