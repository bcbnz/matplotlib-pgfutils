# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from pathlib import Path

from pgfutils import PgfutilsParser, _config, _config_reset


base_dir = Path(__file__).parent.parent.resolve()
share_dir = base_dir / "data" / "share" / "matplotlib-pgfutils"


class TestDataClass:
    def test_data_config(self):
        """Test default configuration in data/ is correct..."""
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

        # Read the config file in data/.
        # Note we use the base class read() method here to avoid some extra
        # error checking in our custom parser which gets in the way of this
        # test being accurately performed.
        data = PgfutilsParser()
        super(PgfutilsParser, data).read(share_dir / "pgfutils.cfg")

        # Compare to the default options.
        assert to_dict(data) == to_dict(_config)
