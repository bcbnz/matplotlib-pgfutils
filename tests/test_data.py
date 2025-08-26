# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from copy import deepcopy
from pathlib import Path

from pgfutils import Config

base_dir = Path(__file__).parent.parent.resolve()
share_dir = base_dir / "data" / "share" / "matplotlib-pgfutils"


class TestDataClass:
    def test_data_config(self):
        """Test default configuration in data/ is correct..."""
        config = Config()

        # Helper function to convert a config object to a dictionary.
        def to_dict(cfg: Config):
            result = {}
            for section in cfg.__annotations__.keys():
                result[section] = getattr(cfg, section)
            return result

        default = deepcopy(to_dict(config))

        # Read the config file in data/.
        config.load(share_dir / "pgfutils.toml")
        from_data = deepcopy(to_dict(config))

        # Compare to the default options.
        assert from_data == default
