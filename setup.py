from setuptools import setup
from pgfutils import __version__

with open("README.md", 'r') as f:
    long_desc = f.read()

setup(
    name="matplotlib-pgfutils",
    version=__version__,
    description="Utilities for generating PGF figures from Matplotlib",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    author="Blair Bonnett",
    author_email="blair.bonnett@gmail.com",
    license="BSD",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    py_modules=["pgfutils"],
    install_requires=[
        "matplotlib >= 1.2",
    ],
    data_files=[
        ['share/matplotlib-pgfutils/', ['extras/pgfutils.cfg', 'extras/latexmkrc']],
    ],
    zip_safe=False,
)
