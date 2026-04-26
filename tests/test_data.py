# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from copy import deepcopy
from pathlib import Path

from pgfutils import Config

base_dir = Path(__file__).parent.parent.resolve()
share_dir = base_dir / "data" / "share" / "matplotlib-pgfutils"


# Helper function to convert a config object to a dictionary.
def to_dict(cfg: Config):
    result = {}
    for section in Config.__annotations__.keys():
        result[section] = getattr(cfg, section)
    return result


class TestDataClass:
    def test_data_config(self, recwarn):
        """Test default configuration in data/ is correct..."""
        config = Config()
        default = deepcopy(to_dict(config))

        # Read the config file in data/.
        config.load(share_dir / "pgfutils.toml")
        from_data = deepcopy(to_dict(config))

        # Compare to the default options.
        assert from_data == default

        # Check there were no extra settings.
        for record in recwarn:
            assert "unknown settings" not in str(record.message)

    def test_doc_default_config(self, tmp_path, recwarn):
        """Test default configuration in docs is correct..."""
        config = Config()
        default = deepcopy(to_dict(config))

        # Read the snippets with the defaults used for the config documentation page.
        toml = []
        for fn in (base_dir / "doc").glob("config_defaults_*.toml"):
            toml.append(fn.read_text())

        # Write it all to a file and parse it.
        cfg = tmp_path / "pgfutils.toml"
        cfg.write_text("\n".join(toml))
        config.load(cfg)
        from_doc = deepcopy(to_dict(config))

        # Compare to the default options.
        assert from_doc == default

        # Check there were no extra settings.
        for record in recwarn:
            assert "unknown settings" not in str(record.message)
