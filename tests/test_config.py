from pgfutils import _config, _config_reset, DimensionError
import os.path
import pytest
from pytest import approx

base = os.path.dirname(__file__)


class TestConfigClass:
    """Configuration parser tests not performed elsewhere."""

    def test_kwargs_unknown(self):
        """Config parser rejects unknown keywords..."""
        _config_reset()
        with pytest.raises(KeyError):
            _config.read_kwargs(unknown_keyword='yellow')


    def test_cfg_unknown(self):
        """Config parser rejects unknown options in config file..."""
        _config_reset()
        with pytest.raises(KeyError):
            _config.read(os.path.join(base, 'sources', 'extra_options.cfg'))


    def test_cfg_rcparams(self):
        """Config parser allows rcParams in config file..."""
        _config_reset()
        _config.read(os.path.join(base, 'sources', 'extra_rcparams.cfg'))
        assert not _config['rcParams'].getboolean('ytick.left'), "ytick.left is incorrect"
        assert _config['rcParams'].getboolean('ytick.right'), "ytick.right is incorrect"


    def test_cfg_unknown_rcparams(self):
        """Config parser rejects unknown options in config file also containing rcParams..."""
        _config_reset()
        with pytest.raises(KeyError):
            _config.read(os.path.join(base, 'sources', 'extra_options_rcparams.cfg'))


    def test_dim_unknown_unit(self):
        """Dimension with unknown unit is rejected..."""
        _config_reset()
        with pytest.raises(DimensionError):
            _config.parsedimension("1.2kg")
        with pytest.raises(DimensionError):
            _config.read_kwargs(text_width='1.2kg')
            _config['tex'].getdimension('text_width')


    def test_dimension_empty(self):
        """Dimension cannot be empty string..."""
        _config_reset()
        with pytest.raises(DimensionError):
            _config.parsedimension("")
        with pytest.raises(DimensionError):
            _config.parsedimension("     ")
        with pytest.raises(DimensionError):
            _config.parsedimension(None)
        with pytest.raises(DimensionError):
            _config.read_kwargs(text_width='')
            _config['tex'].getdimension('text_width')
        with pytest.raises(DimensionError):
            _config.read_kwargs(text_width='    ')
            _config['tex'].getdimension('text_width')


    def test_dimension_not_parsing(self):
        """Dimension rejects invalid strings..."""
        _config_reset()
        with pytest.raises(DimensionError):
            _config.parsedimension("cm1.2")
        with pytest.raises(DimensionError):
            _config.parsedimension("1.2.2cm")
        with pytest.raises(DimensionError):
            _config.read_kwargs(text_width='1.2.2cm')
            _config['tex'].getdimension('text_width')
        with pytest.raises(DimensionError):
            _config.read_kwargs(text_width='cm1.2')
            _config['tex'].getdimension('text_width')


    def test_dimension_inches(self):
        """Dimensions without units are treated as inches..."""
        _config_reset()
        assert _config.parsedimension('7') == approx(7)
        assert _config.parsedimension('2.7') == approx(2.7)
        _config.read_kwargs(text_width='5')
        assert _config['tex'].getdimension('text_width') == approx(5)
        _config.read_kwargs(text_width='5.451')
        assert _config['tex'].getdimension('text_width') == approx(5.451)


    def test_dimension_negative(self):
        """Negative dimensions are rejected..."""
        _config_reset()
        with pytest.raises(DimensionError):
            _config.parsedimension("-1.2")
        with pytest.raises(DimensionError):
            _config.parsedimension("-1.2cm")
        with pytest.raises(DimensionError):
            _config.read_kwargs(text_width="-1.2")
            _config['tex'].getdimension('text_width')
        with pytest.raises(DimensionError):
            _config.read_kwargs(text_width="-1.2cm")
            _config['tex'].getdimension('text_width')


    def test_unknown_tracking_type(self):
        """Unknown tracking types are rejected..."""
        _config_reset()
        with pytest.raises(ValueError):
            _config.in_tracking_dir("unknown", "file.txt")
