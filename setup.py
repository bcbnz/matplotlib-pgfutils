from pathlib import Path
import re

from setuptools import setup

from pgfutils import __version__


# Load the readme as the long description,
# mostly for PyPI's benefit.
with open("README.md", "r") as f:
    long_desc = f.read()

# Turn relative links into absolute ones pointing
# at the file in the master branch of the repository.
long_desc = re.sub(
    r"(\[[^]]+]\()(?!http)(.+\))",
    r"\1https://github.com/bcbnz/matplotlib-pgfutils/blob/master/\2",
    long_desc,
)


# Data files we want to install in /share.
# First, some simple static ones.
data_files = [
    ["share/matplotlib-pgfutils/", ["extras/pgfutils.cfg", "extras/latexmkrc"]],
    ["share/matplotlib-pgfutils/examples", ["extras/examples/README.md"]],
]

# And now to programmatically load the examples.
example_dir = Path(__file__).parent / "extras" / "examples"
install_base = Path("share") / "matplotlib-pgfutils" / "examples"
for obj in example_dir.iterdir():
    if not obj.is_dir():
        continue

    # Find all suitable files in this example directory.
    files = []
    for fn in obj.iterdir():
        if fn.name in {"latexmkrc", "Makefile", "pgfutils.cfg"}:
            files.append(str(fn))
        elif fn.suffix in {".py", ".tex"}:
            files.append(str(fn))

    # And, if we found at least one thing to install,
    # add it to the overall list.
    if files:
        data_files.append([str(install_base / obj.name), files])

# And hand over to setuptools for the rest.
setup(
    name="matplotlib-pgfutils",
    version=__version__,
    description="Utilities for generating PGF figures from Matplotlib",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://github.com/bcbnz/matplotlib-pgfutils",
    author="Blair Bonnett",
    author_email="blair.bonnett@gmail.com",
    license="BSD",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    py_modules=["pgfutils"],
    install_requires=[
        "matplotlib >= 1.2",
    ],
    data_files=data_files,
)
