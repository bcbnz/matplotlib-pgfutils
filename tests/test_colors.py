import pytest
from pgfutils import _config, _config_reset, ColorError
from matplotlib.colors import get_named_colors_mapping

class TestColorClass:
    def test_greyscale(self):
        """Grayscale fraction parsing..."""
        _config_reset()

        # Test a range of valid floats.
        # N.B., Matplotlib uses strings for greyscale.
        for f in (0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
            _config.read_kwargs(figure_background=f)
            assert _config['pgfutils'].getcolor('figure_background') == str(f)

        # The same things as strings.
        for s in ('0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0'):
            _config.read_kwargs(figure_background=s)
            assert _config['pgfutils'].getcolor('figure_background') == s

        # Check numbers outside the valid range.
        for f in (1.01, -1):
            with pytest.raises(ColorError):
                _config.read_kwargs(axes_background=f)
                _config['pgfutils'].getcolor('axes_background')


    def test_named(self):
        """Named color parsing..."""
        _config_reset()

        # Try all known Matplotlib colors.
        for color in get_named_colors_mapping().keys():
            _config.read_kwargs(axes_background=color)
            assert _config['pgfutils'].getcolor('axes_background') == color

        # And check it rejects non-existent named colors.
        with pytest.raises(ColorError):
            _config.read_kwargs(axes_background='nonexistentuglycolor')
            _config['pgfutils'].getcolor('axes_background')
