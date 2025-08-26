# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from matplotlib import rcParams
import pytest

from pgfutils import config, setup_figure


def test_two_columns():
    """Check behaviour for document with two columns..."""
    config.tex["num_columns"] = 2
    config.tex["text_width"] = 8.0
    config.tex["text_height"] = 4.0
    config.tex["columnsep"] = 1

    # Check some simple cases.
    setup_figure(width=1, height=1, columns=None)
    assert rcParams["figure.figsize"] == [
        8,
        4,
    ], "Wrong width for columns=None, width=1."
    setup_figure(width=1, height=1, columns=1)
    assert rcParams["figure.figsize"] == [
        3.5,
        4,
    ], "Wrong width for one column, width=1."
    setup_figure(width=1, height=1, columns=2)
    assert rcParams["figure.figsize"] == [8, 4], "Wrong width for two columns, width=1."

    # And now with some fractional widths.
    setup_figure(width=0.6, height=1, columns=None)
    assert rcParams["figure.figsize"] == [
        4.8,
        4,
    ], "Wrong width for columns=None, width=0.6."
    setup_figure(width=0.5, height=1, columns=1)
    assert rcParams["figure.figsize"] == [
        1.75,
        4,
    ], "Wrong width for one column, width=0.5."
    setup_figure(width=0.85, height=1, columns=2)
    assert rcParams["figure.figsize"] == [
        6.8,
        4,
    ], "Wrong width for two columns, width=0.85."

    # And some error conditions.
    with pytest.raises(ValueError, match="must be at least one"):
        setup_figure(width=1, height=1, columns=-1)
    with pytest.raises(ValueError, match="must be at least one"):
        setup_figure(width=1, height=1, columns=0)
    with pytest.raises(ValueError, match="document has 2 columns"):
        setup_figure(width=1, height=1, columns=3)


def test_three_columns():
    """Check behaviour for document with three columns..."""
    config.tex["num_columns"] = 3
    config.tex["text_width"] = 8.0
    config.tex["text_height"] = 4.0
    config.tex["columnsep"] = 1

    # Check some simple cases.
    setup_figure(width=1, height=1, columns=None)
    assert rcParams["figure.figsize"] == [
        8,
        4,
    ], "Wrong width for columns=None, width=1."
    setup_figure(width=1, height=1, columns=1)
    assert rcParams["figure.figsize"] == [2, 4], "Wrong width for one column, width=1."
    setup_figure(width=1, height=1, columns=2)
    assert rcParams["figure.figsize"] == [5, 4], "Wrong width for two columns, width=1."
    setup_figure(width=1, height=1, columns=3)
    assert rcParams["figure.figsize"] == [
        8,
        4,
    ], "Wrong width for three columns, width=1."

    # And now with some fractional widths.
    setup_figure(width=0.6, height=1, columns=None)
    assert rcParams["figure.figsize"] == [
        4.8,
        4,
    ], "Wrong width for columns=None, width=0.6."
    setup_figure(width=0.5, height=1, columns=1)
    assert rcParams["figure.figsize"] == [
        1,
        4,
    ], "Wrong width for one column, width=0.5."
    setup_figure(width=0.85, height=1, columns=2)
    assert rcParams["figure.figsize"] == [
        4.25,
        4,
    ], "Wrong width for two columns, width=0.85."
    setup_figure(width=0.4, height=1, columns=3)
    assert rcParams["figure.figsize"] == [
        3.2,
        4,
    ], "Wrong width for three columns, width=0.4."

    # And some error conditions.
    with pytest.raises(ValueError, match="must be at least one"):
        setup_figure(width=1, height=1, columns=-1)
    with pytest.raises(ValueError, match="must be at least one"):
        setup_figure(width=1, height=1, columns=0)
    with pytest.raises(ValueError, match="document has 3 columns"):
        setup_figure(width=1, height=1, columns=4)
