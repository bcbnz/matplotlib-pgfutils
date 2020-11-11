import os.path
from pgfutils import _config, _config_reset, PgfutilsParser


class TestExtrasClass:
    def test_extras_config(self):
        """Test default configuration in extras/ is correct..."""
        _config_reset()

        # Helper function to convert a config object to a dictionary.
        # This also strips leading/trailing whitespace in the paths section as
        # all options can take multiline values.
        def to_dict(cfg):
            result = {}
            for section in cfg.sections():
                conv = dict(cfg[section])
                if section == "paths":
                    conv = {k: v.strip() for k, v in conv.items()}
                result[section] = conv
            return result

        # Read the config file in extras/.
        # Note we use the base class read() method here to avoid some extra
        # error checking in our custom parser which gets in the way of this
        # test being accurately performed.
        extras_dir = os.path.join(os.path.dirname(__file__), '..', 'extras')
        extras_dir = os.path.normpath(extras_dir)
        extras = PgfutilsParser()
        super(PgfutilsParser, extras).read(os.path.join(extras_dir, 'pgfutils.cfg'))

        # Compare to the default options.
        assert to_dict(extras) == to_dict(_config)
