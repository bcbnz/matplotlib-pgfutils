import os.path
from pytest import approx
import re
from .utils import build_figure, build_tex, clean_dir

base = os.path.normpath(os.path.dirname(__file__))


def test_fix_raster_paths():
    """Check fix_raster_paths works..."""
    dir = os.path.join(base, "sources", "fix_raster_paths")
    res = build_figure(dir, "figures/noise.py")
    assert res.returncode == 0, "Building tests/sources/fix_raster_paths/figures/noise.pypgf failed."
    res = build_figure(dir, "speckle.py")
    assert res.returncode == 0, "Building tests/sources/fix_raster_paths/speckle.pypgf failed."
    res = build_tex(dir, "document")
    assert res.returncode == 0, "Building tests/sources/fix_raster_paths/document.pdf failed."
    clean_dir(dir)


def test_tracking_fix_raster_paths():
    """Check file tracking works with fix_raster_paths..."""
    dir = os.path.join(base, "sources", "fix_raster_paths")
    res = build_figure(dir, "figures/noise.py", {"PGFUTILS_TRACK_FILES": "1"})
    assert res.returncode == 0, "Building tests/sources/fix_raster_paths/figures/noise.pypgf failed."
    expected = {
        'r:pgfutils.cfg',
        'w:figures/noise-img0.png',
        'w:figures/noise-img1.png',
    }
    actual = set(res.stdout.strip().splitlines())
    assert actual == expected, "Tracked file mismatch."

    res = build_figure(dir, "speckle.py", {"PGFUTILS_TRACK_FILES": "1"})
    assert res.returncode == 0, "Building tests/sources/fix_raster_paths/speckle.pypgf failed."
    expected = {
        'r:pgfutils.cfg',
        'w:speckle-img0.png',
        'w:speckle-img1.png',
    }
    actual = set(res.stdout.strip().splitlines())
    assert actual == expected, "Tracked file mismatch."
    clean_dir(dir)


def test_tikzpicture():
    """Check tikzpicture postprocessing works..."""
    dir = os.path.join(base, "sources", "tikzpicture")
    res = build_figure(dir, "square.py")
    assert res.returncode == 0, "Building tests/sources/tikzpicture/square.pypgf failed."
    res = build_tex(dir, "document_pgf")
    assert res.returncode != 0, "Document should have failed to built without the tikz package."
    res = build_tex(dir, "document_tikz")
    assert res.returncode == 0, "Document failed to build with the tikz package."
    clean_dir(dir)


def test_legend_parameters():
    """Check legend parameters are set..."""
    # Build the image.
    dir = os.path.join(base, "sources", "legend")
    res = build_figure(dir, "legend_only.py")
    assert res.returncode == 0, "Building tests/sources/legend/legend_only.pypgf failed."

    # Go through and find some values of interest.
    text_sizes = []
    current_scope = []
    found_legend_scope = False
    legend_scope = None

    with open("tests/sources/legend/legend_only.pypgf", 'r') as f:
        for line in f:
            line = line.strip()

            # Text: since we've disabled all other sources of writing, this
            # must be due to a legend entry.
            if r'\pgftext' in line:
                text_sizes.extend(map(float, re.findall(r'.+\\fontsize\{([\d.]+)}', line)))

            # Start of a scope.
            elif r'\begin{pgfscope}' in line:
                current_scope = []
                found_legend_scope = False

            # End of a scope.
            elif r'\end{pgfscope}' in line and found_legend_scope:
                legend_scope = list(current_scope)

            # Only the legend contains a background.
            elif r'\definecolor{currentfill}' in line:
                found_legend_scope = True

            # Add the line to the current scope.
            current_scope.append(line)

    # Check the text sizes are correct.
    assert text_sizes == approx([14, 14, 14]), "Legend font sizes are incorrect."

    # No legend found.
    if not legend_scope:
        raise AssertionError("Could not find PGF scope containing legend.")

    # Pull out properties set within the legend scope.
    fill = []
    fillopacity = -1
    stroke = []
    strokeopacity = -1
    linewidth = -1
    for line in legend_scope:
        if r'\definecolor{currentfill}' in line:
            fill = list(map(float, re.findall(r'[\d.]+', line)))
        elif r'\pgfsetfillopacity' in line:
            fillopacity = float(re.findall(r'[\d.]+', line)[0])
        elif r'\definecolor{currentstroke}' in line:
            stroke = list(map(float, re.findall(r'[\d.]+', line)))
        elif r'\pgfsetstrokeopacity' in line:
            strokeopacity = float(re.findall(r'[\d.]+', line)[0])
        elif r'\pgfsetlinewidth' in line:
            linewidth = float(re.findall(r'[\d.]+', line)[0])

    # Now check the values are correct. Note the increased margin for the
    # line size -- the output value often seems to be a wee way off the
    # number. I'd guess this is due to some rounding in the exporter. At
    # the end of the day 0.1 of a point is not that noticeable!
    assert fill == approx([0, 0.5, 1]), "Legend background colour is wrong."
    assert fillopacity == approx(0.7), "Legend background opacity is wrong."
    assert stroke == approx([1, 0.5, 0]), "Legend border colour is wrong."
    assert strokeopacity == approx(0.7), "Legend border opacity is wrong."
    assert linewidth == approx(4, abs=0.1), "Legend border width is wrong."

    # Done.
    clean_dir(dir)
