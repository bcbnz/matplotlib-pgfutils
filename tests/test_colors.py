# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from matplotlib.colors import get_named_colors_mapping
import numpy as np
import pytest

from pgfutils import ColorError, parse_color


class TestColor:
    def test_greyscale(self):
        """Grayscale fraction parsing..."""
        # Test a range of valid floats.
        # N.B., Matplotlib uses strings for greyscale.
        for f in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
            assert parse_color(f) == str(f)
            assert parse_color(str(f)) == str(f)

        # The same things as strings.
        for s in (
            "0.0",
            "0.1",
            "0.2",
            "0.3",
            "0.4",
            "0.5",
            "0.6",
            "0.7",
            "0.8",
            "0.9",
            "1.0",
        ):
            assert parse_color(s) == s

        # Check numbers outside the valid range.
        for f in (1.01, -1):
            with pytest.raises(ColorError, match=r"must be in \[0, 1\]"):
                parse_color(f)

    def test_named(self):
        """Named color parsing..."""
        # Try all known Matplotlib colors.
        for color in get_named_colors_mapping().keys():
            assert parse_color(color) == color

        # And check it rejects non-existent named colors.
        with pytest.raises(ColorError, match="could not interpret .+ as a color"):
            parse_color("some_ugly_color")

    def test_cycle(self):
        """Color cycle parsing..."""
        for i in range(0, 10):
            cycle = "C{0:d}".format(i)
            assert parse_color(cycle) == cycle

    def test_transparent(self):
        """Color parsing supports transparency..."""
        assert parse_color("none") == "none"
        assert parse_color("transparent") == "none"
        assert parse_color("") == "none"

    def test_rgb(self):
        """RGB list/tuple color parsing..."""
        # Generate a set of valid colors. We have to include an alpha channel
        # here as it is always returned from the parser with alpha=1.
        c = np.linspace(0, 1, 5)
        a = (c * 0) + 1.0
        colors = np.stack(np.meshgrid(c, c, c, a), -1).reshape(-1, 4)

        # Check they are accepted. The parser always returns colors as tuples.
        for color in colors:
            list_c = color.tolist()
            tuple_c = tuple(list_c)
            assert parse_color(list_c) == tuple_c
            assert parse_color(tuple_c) == tuple_c

        # Check it fails on channels with invalid values.
        color = [0, 0, 0]
        for channel in range(3):
            for value in (-0.1, 1.2, "a", None):
                color[channel] = value
                with pytest.raises(ColorError):
                    parse_color(color)
            color[channel] = 0

        # And some invalid formats too.
        for value in ("fail", "yes", "no"):
            with pytest.raises(ColorError, match="could not interpret.+as a color"):
                parse_color(value)

    def test_rgba(self):
        """RGBA list/tuple color parsing..."""
        # Generate a set of valid colors.
        c = np.linspace(0, 1, 5)
        colors = np.stack(np.meshgrid(c, c, c, c), -1).reshape(-1, 4)

        # Check they are accepted. The parser always returns colors as tuples.
        for color in colors:
            list_c = color.tolist()
            tuple_c = tuple(list_c)
            assert parse_color(list_c) == tuple_c
            assert parse_color(tuple_c) == tuple_c

        # Check it fails on channels with invalid values.
        color = [0, 0, 0, 0]
        for channel in range(4):
            for value in (-0.1, 1.2, "a", None):
                color[channel] = value
                with pytest.raises(ColorError):
                    parse_color(color)
            color[channel] = 0

        # And some invalid formats too.
        for value in ("fail", "yes", "no"):
            with pytest.raises(ColorError, match="could not interpret.+as a color"):
                parse_color(value)

    def test_invalid_tuples(self):
        """Check RGB/RGBA parsing rejects tuples of invalid length..."""
        with pytest.raises(ColorError):
            parse_color((1,))
        with pytest.raises(ColorError):
            parse_color((1, 1))
        with pytest.raises(ColorError):
            parse_color((1, 1, 1, 1, 1))
