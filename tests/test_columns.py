from pgfutils import setup_figure
from matplotlib import rcParams
import pytest


def test_two_columns():
    """Check behaviour for document with two columns..."""
    params = {'text_width': 8.0, 'text_height': 4, 'num_columns': 2, 'columnsep': 1}

    # Check some simple cases.
    setup_figure(width=1, height=1, columns=None, **params)
    assert rcParams['figure.figsize'] == [8, 4], "Wrong width for columns=None, width=1."
    setup_figure(width=1, height=1, columns=1, **params)
    assert rcParams['figure.figsize'] == [3.5, 4], "Wrong width for one column, width=1."
    setup_figure(width=1, height=1, columns=2, **params)
    assert rcParams['figure.figsize'] == [8, 4], "Wrong width for two columns, width=1."

    # And now with some fractional widths.
    setup_figure(width=0.6, height=1, columns=None, **params)
    assert rcParams['figure.figsize'] == [4.8, 4], "Wrong width for columns=None, width=0.6."
    setup_figure(width=0.5, height=1, columns=1, **params)
    assert rcParams['figure.figsize'] == [1.75, 4], "Wrong width for one column, width=0.5."
    setup_figure(width=0.85, height=1, columns=2, **params)
    assert rcParams['figure.figsize'] == [6.8, 4], "Wrong width for two columns, width=0.85."

    # And some error conditions.
    with pytest.raises(ValueError):
        setup_figure(width=1, height=1, columns=-1, **params)
    with pytest.raises(ValueError):
        setup_figure(width=1, height=1, columns=0, **params)
    with pytest.raises(ValueError):
        setup_figure(width=1, height=1, columns=3, **params)


def test_three_columns():
    """Check behaviour for document with three columns..."""
    params = {'text_width': 8.0, 'text_height': 4, 'num_columns': 3, 'columnsep': 1}

    # Check some simple cases.
    setup_figure(width=1, height=1, columns=None, **params)
    assert rcParams['figure.figsize'] == [8, 4], "Wrong width for columns=None, width=1."
    setup_figure(width=1, height=1, columns=1, **params)
    assert rcParams['figure.figsize'] == [2, 4], "Wrong width for one column, width=1."
    setup_figure(width=1, height=1, columns=2, **params)
    assert rcParams['figure.figsize'] == [5, 4], "Wrong width for two columns, width=1."
    setup_figure(width=1, height=1, columns=3, **params)
    assert rcParams['figure.figsize'] == [8, 4], "Wrong width for three columns, width=1."

    # And now with some fractional widths.
    setup_figure(width=0.6, height=1, columns=None, **params)
    assert rcParams['figure.figsize'] == [4.8, 4], "Wrong width for columns=None, width=0.6."
    setup_figure(width=0.5, height=1, columns=1, **params)
    assert rcParams['figure.figsize'] == [1, 4], "Wrong width for one column, width=0.5."
    setup_figure(width=0.85, height=1, columns=2, **params)
    assert rcParams['figure.figsize'] == [4.25, 4], "Wrong width for two columns, width=0.85."
    setup_figure(width=0.4, height=1, columns=3, **params)
    assert rcParams['figure.figsize'] == [3.2, 4], "Wrong width for three columns, width=0.4."

    # And some error conditions.
    with pytest.raises(ValueError):
        setup_figure(width=1, height=1, columns=-1, **params)
    with pytest.raises(ValueError):
        setup_figure(width=1, height=1, columns=0, **params)
    with pytest.raises(ValueError):
        setup_figure(width=1, height=1, columns=4, **params)
