from pgfutils import setup_figure, _config, _config_reset
import matplotlib
import numpy as np
import os.path
from pytest import approx, raises
from .utils import build_figure, clean_dir

base = os.path.normpath(os.path.dirname(__file__))


class TestSetupFigureClass:
    def test_setup_both_fractions(self):
        """setup_figure() with both sizes fractions..."""
        # Simple case.
        _config_reset()
        setup_figure(width=1, height=1)
        w, h = matplotlib.rcParams['figure.figsize']
        assert w == _config['tex'].getdimension('text_width')
        assert h == _config['tex'].getdimension('text_height')

        # More complicated fractions.
        for m in np.linspace(0.1, 2.1, 13):
            for n in np.linspace(0.1, 2.1, 13):
                _config_reset()
                setup_figure(width=m, height=n)
                w, h = matplotlib.rcParams['figure.figsize']
                assert w == approx(m * _config['tex'].getdimension('text_width'))
                assert h == approx(n * _config['tex'].getdimension('text_height'))


    def test_setup_both_dimensions(self):
        """setup_figure() with both sizes specific dimensions..."""
        # Dimensions and their size in inches.
        dims = {
            '1in': 1,
            '2.5 inch': 2.5,
            '3 inches': 3,
            '2.54cm': 1,
            '1 centimetre': 0.3937,
            '8 centimetres': 3.14961,
            '1.0 centimeter': 0.3937,
            '8.0 centimeters': 3.14961,
            '80mm': 3.14961,
            '200 millimetre': 7.8740,
            '123.4 millimetres': 4.8583,
            '200 millimeter': 7.8740,
            '123.4 millimeters': 4.8583,
            '340pt': 4.7046,
            '120point': 1.6604,
            '960 points': 13.2835,
        }

        # Check each combination.
        for wstr, winch in dims.items():
            for hstr, hinch in dims.items():
                _config_reset()
                setup_figure(width=wstr, height=hstr)
                w, h = matplotlib.rcParams['figure.figsize']
                assert w == approx(winch, rel=1e-3)
                assert h == approx(hinch, rel=1e-3)


    def test_setup_width_fraction(self):
        """setup_figure() with width as a fraction and specific height..."""
        # Dimensions and their size in inches.
        dims = {
            '1in': 1,
            '2.5 inch': 2.5,
            '3 inches': 3,
            '2.54cm': 1,
            '1 centimetre': 0.3937,
            '8 centimetres': 3.14961,
            '1.0 centimeter': 0.3937,
            '8.0 centimeters': 3.14961,
            '80mm': 3.14961,
            '200 millimetre': 7.8740,
            '123.4 millimetres': 4.8583,
            '200 millimeter': 7.8740,
            '123.4 millimeters': 4.8583,
            '340pt': 4.7046,
            '120point': 1.6604,
            '960 points': 13.2835,
        }

        # Check various combinations.
        for m in np.linspace(0.3, 2.5, 17):
            for hstr, hinch in dims.items():
                _config_reset()
                setup_figure(width=m, height=hstr)
                w, h = matplotlib.rcParams['figure.figsize']
                assert w == approx(m * _config['tex'].getdimension('text_width'))
                assert h == approx(hinch, rel=1e-3)


    def test_setup_height_fraction(self):
        """setup_figure() with specific width and height as a fraction..."""
        # Dimensions and their size in inches.
        dims = {
            '1in': 1,
            '2.5 inch': 2.5,
            '3 inches': 3,
            '2.54cm': 1,
            '1 centimetre': 0.3937,
            '8 centimetres': 3.14961,
            '1.0 centimeter': 0.3937,
            '8.0 centimeters': 3.14961,
            '80mm': 3.14961,
            '200 millimetre': 7.8740,
            '123.4 millimetres': 4.8583,
            '200 millimeter': 7.8740,
            '123.4 millimeters': 4.8583,
            '340pt': 4.7046,
            '120point': 1.6604,
            '960 points': 13.2835,
        }

        # Check various combinations.
        for wstr, winch in dims.items():
            for n in np.linspace(0.3, 2.5, 17):
                _config_reset()
                setup_figure(width=wstr, height=n)
                w, h = matplotlib.rcParams['figure.figsize']
                assert w == approx(winch, rel=1e-3)
                assert h == approx(n * _config['tex'].getdimension('text_height'))


    def test_kwargs_overrides(self):
        """Test setup_figure() kwargs override configuration file..."""
        dir = os.path.join(base, "sources", "kwargs")

        # Helper to parse a fill color from a pypgf file.
        def get_fill_color(fn):
            with open(fn, 'r') as f:
                for line in f:
                    if 'currentfill' not in line:
                        continue
                    line = line.replace(r'\definecolor{currentfill}{rgb}{', '')
                    line = line.replace(r'}%', '')
                    return tuple(map(float, line.split(',')))

        # Check the default (pgfutils.cfg) fill color is in use.
        res = build_figure(dir, 'default.py')
        assert res.returncode == 0, "Failed to run test/sources/kwargs/default.py."
        assert get_fill_color('tests/sources/kwargs/default.pypgf') == approx((0, 0, 1)), \
            "Default background fill should be blue, (0, 0, 1)."

        # And now check we can override this using kwargs.
        res = build_figure(dir, 'overridden.py')
        assert res.returncode == 0, "Failed to run test/sources/kwargs/overridden.py."
        assert get_fill_color('tests/sources/kwargs/overridden.pypgf') == approx((1, 0, 0)), \
            "Overridden background fill should be red, (1, 0, 0)."

        # Done.
        clean_dir(dir)


    def test_kwargs_rejects_unknown(self):
        """Test setup_figure() rejects unknown configuration options..."""
        with raises(KeyError):
            setup_figure(width=1, height=1, border_width=3)
