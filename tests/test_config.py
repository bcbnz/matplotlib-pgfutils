# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from pathlib import Path

import pytest

from pgfutils import _config, _config_reset

base = Path(__file__).parent


class TestConfigClass:
    """Configuration parser tests not performed elsewhere."""

    def test_kwargs_unknown(self):
        """Config parser rejects unknown keywords..."""
        _config_reset()
        with pytest.raises(KeyError):
            _config.read_kwargs(unknown_keyword="yellow")

    def test_cfg_unknown(self):
        """Config parser rejects unknown options in config file..."""
        _config_reset()
        with pytest.raises(KeyError):
            _config.read(base / "sources" / "extra_options.cfg")

    def test_cfg_rcparams(self):
        """Config parser allows rcParams in config file..."""
        _config_reset()
        _config.read(base / "sources" / "extra_rcparams.cfg")
        assert not _config["rcParams"].getboolean("ytick.left"), (
            "ytick.left is incorrect"
        )
        assert _config["rcParams"].getboolean("ytick.right"), "ytick.right is incorrect"

    def test_cfg_unknown_rcparams(self):
        """Config parser rejects unknown options in file also containing rcParams..."""
        _config_reset()
        with pytest.raises(KeyError):
            _config.read(base / "sources" / "extra_options_rcparams.cfg")

    def test_unknown_tracking_type(self):
        """Unknown tracking types are rejected..."""
        _config_reset()
        with pytest.raises(ValueError):
            _config.in_tracking_dir("unknown", "file.txt")
