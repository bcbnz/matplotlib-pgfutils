import os.path
from pgfutils import _config, _config_reset, PgfutilsParser


class TestExtrasClass:
    def test_extras_config(self):
        """Test default configuration in extras/ is correct..."""
        _config_reset()

        # Helper function to convert a config object to a dictionary.
        def to_dict(cfg):
            result = {}
            for section in cfg.sections():
                result[section] = dict(cfg[section])
            return result

        # Read the config file in extras/.
        extras_dir = os.path.join(os.path.dirname(__file__), '..', 'extras')
        extras_dir = os.path.normpath(extras_dir)
        extras = PgfutilsParser()
        extras.read(os.path.join(extras_dir, 'pgfutils.cfg'))

        # Compare to the default options.
        assert to_dict(extras) == to_dict(_config)
