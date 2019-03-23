from pgfutils import setup_figure, save
import os
import pytest


class TestMiscClass:
    def test_save_with_figure(self):
        """Test save() works when given an explicit figure instance..."""
        setup_figure(width=1, height=1)
        from matplotlib import pyplot as plt
        fig = plt.figure()
        save(fig)
        os.unlink("tests/test_misc.pypgf")


    def test_save_with_nonfigure_fails(self):
        """Test save() fails when given a non-figure object..."""
        setup_figure(width=1, height=1)
        with pytest.raises(AttributeError):
            save(self)
