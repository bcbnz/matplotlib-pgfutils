import os
import os.path
import subprocess
import sys


class TestTexClass:
    def expand_filename(self, filename):
        fn = os.path.normpath(os.path.dirname(__file__))
        fn = os.path.join(fn, 'tex', filename)
        return fn


    def run_script(self, wd, filename):
        # Generate an environment to run the script in. This is a copy of our
        # environment with the path exported using absolute paths. This ensures
        # the same copy of the module etc. are used.
        env = dict(os.environ)
        env['PYTHONPATH'] = ':'.join(os.path.normpath(p) for p in sys.path)

        # Run the script.
        cwd = os.getcwd()
        os.chdir(self.expand_filename(wd))
        res = subprocess.run([sys.executable, filename], text=True, env=env,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.chdir(cwd)
        return res


    def run_tex(self, wd, filename):
        cwd = os.getcwd()
        os.chdir(self.expand_filename(wd))
        res = subprocess.run(['xelatex', filename], text=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.chdir(cwd)
        return res


    def test_fix_raster_paths(self):
        """Check fix_raster_paths works..."""
        res = self.run_script("fix_raster_paths", "figures/noise.py")
        assert res.returncode == 0, "Building tests/tex/fix_raster_paths/figures/noise.pypgf failed."
        res = self.run_script("fix_raster_paths", "speckle.py")
        assert res.returncode == 0, "Building tests/tex/fix_raster_paths/speckle.pypgf failed."
        res = self.run_tex("fix_raster_paths", "document")
        assert res.returncode == 0, "Building tests/tex/fix_raster_paths/document.pdf failed."


    def test_tikzpicture(self):
        """Check tikzpicture postprocessing works..."""
        res = self.run_script("tikzpicture", "square.py")
        assert res.returncode == 0, "Building tests/tex/tikzpicture/square.pypgf failed."
        res = self.run_tex("tikzpicture", "document_pgf")
        assert res.returncode != 0, "Document should have failed to built without the tikz package."
        res = self.run_tex("tikzpicture", "document_tikz")
        assert res.returncode == 0, "Document failed to build with the tikz package."
