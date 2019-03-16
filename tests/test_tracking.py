import os
import os.path
import subprocess
import sys
import tempfile


class TestTrackingClass:
    def expand_filename(self, filename):
        fn = os.path.normpath(os.path.dirname(__file__))
        fn = os.path.join(fn, 'tracking_scripts', filename)
        return fn


    def run_script(self, filename, dest):
        # Generate an environment to run the script in. This is a copy of our
        # environment with the path exported using absolute paths. This ensures
        # the same copy of the module etc. are used.
        env = dict(os.environ)
        env['PYTHONPATH'] = ':'.join(os.path.normpath(p) for p in sys.path)

        # Add our tracking destination.
        env['PGFUTILS_TRACK_FILES'] = str(dest)

        # Run the script.
        fn = self.expand_filename(filename)
        return subprocess.run([sys.executable, fn], text=True, env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    def cleanup(self):
        dirname = os.path.normpath(os.path.dirname(__file__))
        dirname = os.path.join(dirname, 'tracking_scripts')
        for root, dirs, files in os.walk(dirname):
            for fn in files:
                base, ext = os.path.splitext(fn)
                if ext in {'.pypgf', '.png'}:
                    os.unlink(os.path.join(root, fn))
                if fn == 'tracking.test.results':
                    os.unlink(os.path.join(root, fn))


    def test_simple_stdout(self):
        """File tracking to stdout with no dependencies or rasterisation..."""
        # Run the script and check no files were reported.
        res = self.run_script('simple.py', 1)
        assert res.returncode == 0
        assert len(res.stdout.strip()) == 0
        self.cleanup()


    def test_simple_stderr(self):
        """File tracking to stderr with no dependencies or rasterisation..."""
        # Run the script and check no files were reported.
        res = self.run_script('simple.py', 2)
        assert res.returncode == 0
        assert len(res.stderr.strip()) == 0
        self.cleanup()


    def test_simple_file(self):
        """File tracking to file with no dependencies or rasterisation..."""
        # Run the script and check no files were reported.
        tfn = self.expand_filename('tracking.test.results')
        res = self.run_script('simple.py', tfn)
        assert res.returncode == 0
        stat = os.stat(tfn)
        assert stat.st_size == 0
        self.cleanup()


    def test_rasterisation_stdout(self):
        """File tracking to stdout with rasterised image..."""
        # Run the script.
        res = self.run_script('rasterisation.py', 1)
        assert res.returncode == 0

        # Check the expected raster filename is reported.
        fn = 'tests/tracking_scripts/rasterisation-img0.png'
        assert res.stdout.strip() == 'w:' + fn

        self.cleanup()


    def test_rasterisation_stderr(self):
        """File tracking to stderr with rasterised image..."""
        # Run the script.
        res = self.run_script('rasterisation.py', 2)
        assert res.returncode == 0

        # Check the expected raster filename is reported.
        fn = 'tests/tracking_scripts/rasterisation-img0.png'
        assert res.stderr.strip() == 'w:' + fn

        self.cleanup()


    def test_rasterisation_file(self):
        """File tracking to file with rasterised image..."""
        # Run the script.
        tfn = self.expand_filename('tracking.test.results')
        res = self.run_script('rasterisation.py', tfn)
        assert res.returncode == 0

        # Check the expected raster filename is reported.
        fn = 'tests/tracking_scripts/rasterisation-img0.png'
        with open(tfn, 'r') as f:
            assert f.read().strip() == 'w:' + fn

        self.cleanup()


    def test_loadtxt_stdout(self):
        """File tracking to stdout with loadtxt dependency..."""
        # Run the script.
        res = self.run_script('dependency_loadtxt.py', 1)
        assert res.returncode == 0

        # Check the expected dependency filename is reported.
        fn = 'tests/tracking_scripts/scatter.csv'
        assert res.stdout.strip() == 'r:' + fn

        self.cleanup()


    def test_loadtxt_stderr(self):
        """File tracking to stderr with loadtxt dependency..."""
        # Run the script.
        res = self.run_script('dependency_loadtxt.py', 2)
        assert res.returncode == 0

        # Check the expected dependency filename is reported.
        fn = 'tests/tracking_scripts/scatter.csv'
        assert res.stderr.strip() == 'r:' + fn

        self.cleanup()


    def test_loadtxt_file(self):
        """File tracking to file with loadtxt dependency..."""
        # Run the script.
        tfn = self.expand_filename('tracking.test.results')
        res = self.run_script('dependency_loadtxt.py', tfn)
        assert res.returncode == 0

        # Check the expected dependency filename is reported.
        fn = 'tests/tracking_scripts/scatter.csv'
        with open(tfn, 'r') as f:
            assert f.read().strip() == 'r:' + fn

        self.cleanup()


    def test_load_stdout(self):
        """File tracking to stdout with NumPy format dependency..."""
        # Run the script.
        res = self.run_script('dependency_npy.py', 1)
        assert res.returncode == 0

        # Check the expected dependency filename is reported.
        fn = 'tests/tracking_scripts/noise.npy'
        assert res.stdout.strip() == 'r:' + fn

        self.cleanup()


    def test_load_stderr(self):
        """File tracking to stderr with NumPy format dependency..."""
        # Run the script.
        res = self.run_script('dependency_npy.py', 2)
        assert res.returncode == 0

        # Check the expected dependency filename is reported.
        fn = 'tests/tracking_scripts/noise.npy'
        assert res.stderr.strip() == 'r:' + fn

        self.cleanup()


    def test_load_file(self):
        """File tracking to file with NumPy format dependency..."""
        # Run the script.
        tfn = self.expand_filename('tracking.test.results')
        res = self.run_script('dependency_npy.py', tfn)
        assert res.returncode == 0

        # Check the expected dependency filename is reported.
        fn = 'tests/tracking_scripts/noise.npy'
        with open(tfn, 'r') as f:
            assert f.read().strip() == 'r:' + fn

        self.cleanup()


    def test_multi_stdout(self):
        """File tracking to stdout with multiple dependencies and rasterisation..."""
        # Run the script.
        res = self.run_script('multi.py', 1)
        assert res.returncode == 0

        # Check the results are as expected.
        expected = {
            'r:tests/tracking_scripts/noise.npy',
            'r:tests/tracking_scripts/scatter.csv',
            'w:tests/tracking_scripts/multi-img0.png',
            'w:tests/tracking_scripts/multi-img1.png',
        }
        actual = set(res.stdout.strip().splitlines())
        assert actual == expected

        self.cleanup()


    def test_multi_stderr(self):
        """File tracking to stderr with multiple dependencies and rasterisation..."""
        # Run the script.
        res = self.run_script('multi.py', 2)
        assert res.returncode == 0

        # Check the results are as expected.
        expected = {
            'r:tests/tracking_scripts/noise.npy',
            'r:tests/tracking_scripts/scatter.csv',
            'w:tests/tracking_scripts/multi-img0.png',
            'w:tests/tracking_scripts/multi-img1.png',
        }
        actual = set(res.stderr.strip().splitlines())
        assert actual == expected

        self.cleanup()


    def test_multi_file(self):
        """File tracking to file with multiple dependencies and rasterisation..."""
        # Run the script.
        tfn = self.expand_filename('tracking.test.results')
        res = self.run_script('multi.py', tfn)
        assert res.returncode == 0

        # Check the results are as expected.
        expected = {
            'r:tests/tracking_scripts/noise.npy',
            'r:tests/tracking_scripts/scatter.csv',
            'w:tests/tracking_scripts/multi-img0.png',
            'w:tests/tracking_scripts/multi-img1.png',
        }
        with open(tfn, 'r') as f:
            actual = set(f.read().strip().splitlines())
        assert actual == expected

        self.cleanup()


    def test_ignore_non_image_binary(self):
        """File tracking ignores non-image binary written files..."""
        # Run the script.
        res = self.run_script('simple_binary_nonimage.py', 1)
        assert res.returncode == 0, "Running tests/tracking_scripts/simple_binary_nonimage.py failed."
        assert os.path.exists("tests/tracking_scripts/test.npy"), "Test output not written."
        assert len(res.stdout.strip()) == 0, "Tracking output was not empty."
        self.cleanup()
        os.unlink("tests/tracking_scripts/test.npy")


    def test_ignore_non_binary(self):
        """File tracking ignores non-binary written files..."""
        # Run the script.
        res = self.run_script('simple_nonbinary.py', 1)
        assert res.returncode == 0, "Running tests/tracking_scripts/simple_nonbinary.py failed."
        assert os.path.exists("tests/tracking_scripts/test.txt"), "Test output not written."
        assert len(res.stdout.strip()) == 0, "Tracking output was not empty."
        self.cleanup()
        os.unlink("tests/tracking_scripts/test.txt")


    def test_nonfile_opener(self):
        """File tracking ignores openers that don't return file objects..."""
        res = self.run_script('simple_nonfile.py', 1)
        assert res.returncode == 0, "Running tests/tracking_scripts/simple_nonfile.py failed."
        assert os.path.exists("tests/tracking_scripts/test_nonfile.png"), "Test output not written."
        assert len(res.stdout.strip()) == 0, "Tracking output was not empty."
        self.cleanup()


    def test_fdopen(self):
        """File tracking ignores file objects from os.fdopen..."""
        res = self.run_script('simple_fdopen.py', 1)
        assert res.returncode == 0, "Running tests/tracking_scripts/simple_fdopen.py failed."
        assert os.path.exists("tests/tracking_scripts/test_fdopen.png"), "Test output not written."
        assert len(res.stdout.strip()) == 0, "Tracking output was not empty."
        self.cleanup()


    def test_nonproject(self):
        """File tracking ignores files written outside top-level directory..."""
        res = self.run_script('simple_nonproject.py', 1)
        assert res.returncode == 0, "Running tests/tracking_scripts/simple_nonproject.py failed."
        tfn = os.path.join(tempfile.gettempdir(), "test_nonproject.png")
        assert os.path.exists(tfn), "Test output not written."
        assert len(res.stdout.strip()) == 0, "Tracking output was not empty."
        self.cleanup()
        os.unlink(tfn)
