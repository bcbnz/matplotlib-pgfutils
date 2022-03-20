from pathlib import Path

from .utils import build_pypgf


srcdir = Path(__file__).parent / "sources" / "pythonpath"


def test_python_path():
    """Check sys.path can be modified..."""
    with build_pypgf(srcdir, "using_custom_lib.py") as res:
        assert (
            res.returncode == 0
        ), f"{srcdir / 'using_custom_lib.py'} could not be built."
