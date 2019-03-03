from pgfutils import setup_figure, _config, _config_reset
import matplotlib
import numpy as np
from pytest import approx

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
