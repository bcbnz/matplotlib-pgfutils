import os.path
from .utils import build_figure, clean_dir
import pytest

srcdir = os.path.join(os.path.normpath(os.path.dirname(__file__)), "sources", "pythonpath")


def test_python_path():
    """Check sys.path can be modified..."""
    res = build_figure(srcdir, "using_custom_lib.py")
    assert res.returncode == 0, "tests/sources/pythonpath/using_custom_lib.py could not be built."
    clean_dir(srcdir)
