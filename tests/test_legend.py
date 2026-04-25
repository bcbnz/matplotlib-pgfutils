# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from pathlib import Path
import re
from typing import TypedDict

from pytest import approx

from .utils import build_pypgf

srcdir = Path(__file__).parent.resolve() / "sources" / "legend"


class Legend(TypedDict):
    text_sizes: list[float]
    fill: list[float]
    fillopacity: float
    stroke = list[float]
    strokeopacity: float
    linewidth: float


def extract_legend(fn: Path) -> Legend | None:
    # Go through and find some values of interest.
    text_sizes = []
    current_scope = []
    found_legend_scope = False
    legend_scope = None

    for line in fn.read_text().splitlines():
        line = line.strip()

        # Text: since we've disabled all other sources of writing, this
        # must be due to a legend entry.
        if r"\pgftext" in line:
            text_sizes.extend(map(float, re.findall(r".+\\fontsize\{([\d.]+)}", line)))

        # Start of a scope.
        elif r"\begin{pgfscope}" in line:
            current_scope = []
            found_legend_scope = False

        # End of a scope.
        elif r"\end{pgfscope}" in line and found_legend_scope:
            legend_scope = list(current_scope)

        # Only the legend contains a background.
        elif r"\definecolor{currentfill}" in line:
            found_legend_scope = True

        # Add the line to the current scope.
        current_scope.append(line)

    if legend_scope is None:
        return None

    # Pull out properties set within the legend scope.
    legend: Legend = {
        "text_sizes": text_sizes,
        "fill": [],
        "fillopacity": -1,
        "stroke": [],
        "strokeopacity": -1,
        "linewidth": -1,
    }
    for line in legend_scope:
        if r"\definecolor{currentfill}" in line:
            legend["fill"] = list(map(float, re.findall(r"[\d.]+", line)))
        elif r"\pgfsetfillopacity" in line:
            legend["fillopacity"] = float(re.findall(r"[\d.]+", line)[0])
        elif r"\definecolor{currentstroke}" in line:
            legend["stroke"] = list(map(float, re.findall(r"[\d.]+", line)))
        elif r"\pgfsetstrokeopacity" in line:
            legend["strokeopacity"] = float(re.findall(r"[\d.]+", line)[0])
        elif r"\pgfsetlinewidth" in line:
            legend["linewidth"] = float(re.findall(r"[\d.]+", line)[0])

    return legend


def test_legend_parameters():
    """Check legend parameters are set..."""
    with build_pypgf(srcdir, "legend_only.py") as res:
        assert res.returncode == 0, f"Building {srcdir / 'legend_only.pypgf'} failed."

        # Extract the legend.
        legend = extract_legend(srcdir / "legend_only.pypgf")

        # Check the text sizes are correct.
        assert legend["text_sizes"] == approx([14, 14, 14]), "incorrect font sizes"

        # Now check the values are correct. Note the increased margin for the
        # line size -- the output value often seems to be a wee way off the
        # number. I'd guess this is due to some rounding in the exporter. At
        # the end of the day 0.1 of a point is not that noticeable!
        assert legend["fill"] == approx([0, 0.5, 1]), "incorrect background colour"
        assert legend["fillopacity"] == approx(0.7), "incorrect background opacity"
        assert legend["stroke"] == approx([1, 0.5, 0]), "incorrect border colour"
        assert legend["strokeopacity"] == approx(0.7), "incorrect border opacity"
        assert legend["linewidth"] == approx(4, abs=0.1), "incorrect border width"


def test_legend_in_plot():
    """Check plot with legend..."""
    with build_pypgf(srcdir, "plot_with_legend.py") as res:
        assert res.returncode == 0, (
            f"Building {srcdir / 'plot_with_legend.pypgf'} failed."
        )

        # Extract the legend.
        legend = extract_legend(srcdir / "plot_with_legend.pypgf")

        # Check the text sizes are correct.
        assert legend["text_sizes"] == approx([14, 14, 14]), "incorrect font sizes"

        # Now check the values are correct. Note the increased margin for the
        # line size -- the output value often seems to be a wee way off the
        # number. I'd guess this is due to some rounding in the exporter. At
        # the end of the day 0.1 of a point is not that noticeable!
        assert legend["fill"] == approx([0, 0.5, 1]), "incorrect background colour"
        assert legend["fillopacity"] == approx(0.7), "incorrect background opacity"
        assert legend["stroke"] == approx([1, 0.5, 0]), "incorrect border colour"
        assert legend["strokeopacity"] == approx(0.7), "incorrect border opacity"
        assert legend["linewidth"] == approx(4, abs=0.1), "incorrect border width"


def test_separate_legend():
    """Check plot with separate legend..."""
    with build_pypgf(srcdir, "plot_with_separate_legend.py") as res:
        assert res.returncode == 0, (
            f"Building {srcdir / 'plot_with_separate_legend.pypgf'} failed."
        )

        # Should be no legend in main figure.
        legend = extract_legend(srcdir / "plot_with_separate_legend.pypgf")
        assert legend is None, "legend retained in main figure"

        # Get the legend from the separate output.
        legend = extract_legend(srcdir / "plot_with_separate_legend_legend0.pypgf")

        # Check the text sizes are correct.
        assert legend["text_sizes"] == approx([14, 14, 14]), "incorrect font sizes"

        # Now check the values are correct. Note the increased margin for the
        # line size -- the output value often seems to be a wee way off the
        # number. I'd guess this is due to some rounding in the exporter. At
        # the end of the day 0.1 of a point is not that noticeable!
        assert legend["fill"] == approx([0, 0.5, 1]), "incorrect background colour"
        assert legend["fillopacity"] == approx(0.7), "incorrect background opacity"
        assert legend["stroke"] == approx([1, 0.5, 0]), "incorrect border colour"
        assert legend["strokeopacity"] == approx(0.7), "incorrect border opacity"
        assert legend["linewidth"] == approx(4, abs=0.1), "incorrect border width"
