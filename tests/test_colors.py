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


    def test_cycle(self):
        """Color cycle parsing..."""
        _config_reset()

        for i in range(0, 10):
            cycle = "C{0:d}".format(i)
            _config.read_kwargs(axes_background=cycle)
            assert _config['pgfutils'].getcolor('axes_background') == cycle


    def test_transparent(self):
        """Color parsing supports transparency..."""
        _config_reset()
        _config.read_kwargs(axes_background='none')
        assert _config['pgfutils'].getcolor('axes_background') == 'none'
        _config.read_kwargs(axes_background='transparent')
        assert _config['pgfutils'].getcolor('axes_background') == 'none'
        _config.read_kwargs(axes_background='')
        assert _config['pgfutils'].getcolor('axes_background') == 'none'


    def test_rgb(self):
        """RGB list/tuple color parsing..."""
        _config_reset()

        # Generate a set of valid colors. We have to include an alpha channel
        # here as it is always returned from the parser with alpha=1.
        import numpy as np
        c = np.linspace(0, 1, 5)
        a = (c * 0) + 1.0
        colors = np.stack(np.meshgrid(c, c, c, a), -1).reshape(-1, 4)

        # Check they are accepted. The parser always returns colors as tuples.
        for color in colors:
            l = list(color)
            t = tuple(color)
            _config.read_kwargs(figure_background=str(l[:-1]))
            assert _config['pgfutils'].getcolor('figure_background') == t
            _config.read_kwargs(axes_background=str(t[:-1]))
            assert _config['pgfutils'].getcolor('axes_background') == t

        # Check it fails on channels with invalid values.
        color = [0, 0, 0]
        for channel in range(3):
            for value in (-0.1, 1.2, 'a', True, False, None):
                with pytest.raises(ColorError):
                    color[channel] = value
                    _config.read_kwargs(axes_background=color)
                    _config['pgfutils'].getcolor('axes_background')
            color[channel] = 0

        # And some invalid formats too.
        for value in ('1,1,1', 'fail', 'yes', 'no'):
            with pytest.raises(ColorError):
                _config.read_kwargs(axes_background=value)
                _config['pgfutils'].getcolor('axes_background')


    def test_rgba(self):
        """RGBA list/tuple color parsing..."""
        _config_reset()

        # Generate a set of valid colors.
        import numpy as np
        c = np.linspace(0, 1, 5)
        colors = np.stack(np.meshgrid(c, c, c, c), -1).reshape(-1, 4)

        # Check they are accepted. The parser always returns colors as tuples.
        for color in colors:
            l = list(color)
            t = tuple(color)
            _config.read_kwargs(figure_background=str(l))
            assert _config['pgfutils'].getcolor('figure_background') == t
            _config.read_kwargs(axes_background=str(t))
            assert _config['pgfutils'].getcolor('axes_background') == t

        # Check it fails on channels with invalid values.
        color = [0, 0, 0, 0]
        for channel in range(4):
            for value in (-0.1, 1.2, 'a', True, False, None):
                with pytest.raises(ColorError):
                    color[channel] = value
                    _config.read_kwargs(axes_background=color)
                    _config['pgfutils'].getcolor('axes_background')
            color[channel] = 0

        # And some invalid formats too.
        for value in ('1,1,1', 'fail', 'yes', 'no'):
            with pytest.raises(ColorError):
                _config.read_kwargs(axes_background=value)
                _config['pgfutils'].getcolor('axes_background')


    def test_invalid_tuples(self):
        """Check RGB/RGBA parsing rejects tuples of invalid length..."""
        _config_reset()
        with pytest.raises(ColorError):
            _config.read_kwargs(axes_background='(1,)')
            _config['pgfutils'].getcolor('axes_background')
        with pytest.raises(ColorError):
            _config.read_kwargs(axes_background='(1,1)')
            _config['pgfutils'].getcolor('axes_background')
        with pytest.raises(ColorError):
            _config.read_kwargs(axes_background='(1,1,1,1,1)')
            _config['pgfutils'].getcolor('axes_background')
