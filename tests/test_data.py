# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from copy import deepcopy
from pathlib import Path
import tomllib

import pytest

from pgfutils import Config, ConfigError

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
            assert "unknown sections" not in str(record.message)
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
            assert "unknown sections" not in str(record.message)
            assert "unknown settings" not in str(record.message)

    @pytest.mark.parametrize("fn", ["config.md", "file_tracking.md"])
    def test_doc_config_snippets(self, fn, recwarn):
        """Check configuration snippets in docs can be loaded..."""
        # Look for each block of TOML code.
        blocks = []
        current = []
        in_block = False
        for line in (base_dir / "doc" / fn).read_text().splitlines():
            line = line.strip()

            # Start of a TOML block.
            if line in {"```toml", "``` toml"}:
                in_block = True
                continue

            # End of any block.
            if line == "```":
                in_block = False
                if current:
                    blocks.append(list(current))
                    current.clear()
                continue

            # Line in a TOML block. If the block loads its content from external files,
            # we skip the block as they are tested elsewhere.
            if in_block:
                if "--8<--" in line:
                    in_block = False
                    current.clear()
                    continue
                current.append(line)

        # Parse each block as TOML and attempt to update a configuration object with it.
        for block in blocks:
            config = Config()
            block_str = "\n".join(block)
            block_dict = tomllib.loads(block_str)
            try:
                config.update(block_dict)
            except ConfigError as e:
                raise AssertionError(f"{block_str}: {e}")

            # Check there were no extra settings.
            for record in recwarn:
                msg = str(record.message)
                if "unknown sections" in msg:
                    raise AssertionError(f"{block_str}: {msg}")
                if "unknown settings" in msg:
                    raise AssertionError(f"{block_str}: {msg}")
            recwarn.clear()
