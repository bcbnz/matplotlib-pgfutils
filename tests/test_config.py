# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from pathlib import Path

import pytest

from pgfutils import Config

base = Path(__file__).parent


class TestConfigClass:
    """Configuration parser tests not performed elsewhere."""

    def test_kwargs_unknown(self):
        """Config parser warns about unknown keys..."""
        config = Config(load_file=False)
        with pytest.warns(UserWarning, match="unknown settings.+unknown_key"):
            config.update({"pgfutils": {"unknown_key": "yellow"}})

    def test_cfg_unknown(self):
        """Config parser warns about unknown keys in config file..."""
        config = Config(load_file=False)
        with pytest.warns(UserWarning, match="unknown settings.+margin"):
            config.load(base / "sources" / "extra_options.toml")

    def test_cfg_rcparams(self):
        """Config parser allows rcParams in config file..."""
        config = Config(load_file=False)
        config.load(base / "sources" / "extra_rcparams.toml")
        assert not config.rcparams["ytick.left"], "ytick.left is incorrect"
        assert config.rcparams["ytick.right"], "ytick.right is incorrect"

    def test_cfg_unknown_rcparams(self):
        """Config parser warns about unknown keys in file also containing rcParams..."""
        config = Config(load_file=False)
        with pytest.warns(UserWarning, match="unknown settings.+margin"):
            config.load(base / "sources" / "extra_options_rcparams.toml")
