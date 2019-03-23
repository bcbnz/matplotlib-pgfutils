from pgfutils import setup_figure, save
import os
import os.path
import pytest
from .utils import build_figure, clean_dir


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


    def test_readme_example(self):
        """Check example in README can be built..."""
        # Figure out some paths.
        base = os.path.dirname(__file__)
        rfn = os.path.join(base, '..', 'README.md')
        src = os.path.join(base, 'sources')
        sfn = os.path.join(src, 'readme.py')

        # Extract the example from the README.
        with open(rfn, 'r') as readme, open(sfn, 'w') as script:
            in_script = False
            for line in readme:
                sline = line.rstrip()
                if in_script:
                    if sline == '```':
                        break
                    script.write(line)
                else:
                    if sline == '```python':
                        in_script = True

        # Confirm it builds.
        res = build_figure(src, 'readme.py')
        assert res.returncode == 0, "Could not build README example."
        clean_dir(src)
        os.unlink(sfn)
