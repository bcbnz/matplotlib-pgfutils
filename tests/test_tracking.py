import os
import os.path
from .utils import build_figure, build_tex
import tempfile

dirname = os.path.join(os.path.normpath(os.path.dirname(__file__)), "tracking_scripts")


class TestTrackingClass:
    def cleanup(self):
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
        res = build_figure(dirname, 'simple.py', {'PGFUTILS_TRACK_FILES': '1'})
        assert res.returncode == 0
        assert len(res.stdout.strip()) == 0
        self.cleanup()


    def test_simple_stderr(self):
        """File tracking to stderr with no dependencies or rasterisation..."""
        # Run the script and check no files were reported.
        res = build_figure(dirname, 'simple.py', {'PGFUTILS_TRACK_FILES': '2'})
        assert res.returncode == 0
        assert len(res.stderr.strip()) == 0
        self.cleanup()


    def test_simple_file(self):
        """File tracking to file with no dependencies or rasterisation..."""
        # Run the script and check no files were reported.
        tfn = os.path.join(dirname, 'tracking.test.results')
        res = build_figure(dirname, 'simple.py', {'PGFUTILS_TRACK_FILES': tfn})
        assert res.returncode == 0
        stat = os.stat(tfn)
        assert stat.st_size == 0
        self.cleanup()


    def test_rasterisation_stdout(self):
        """File tracking to stdout with rasterised image..."""
        # Run the script.
        res = build_figure(dirname, 'rasterisation.py', {'PGFUTILS_TRACK_FILES': '1'})
        assert res.returncode == 0

        # Check the expected raster filename is reported.
        fn = 'rasterisation-img0.png'
        assert res.stdout.strip() == 'w:' + fn

        self.cleanup()


    def test_rasterisation_stderr(self):
        """File tracking to stderr with rasterised image..."""
        # Run the script.
        res = build_figure(dirname, 'rasterisation.py', {'PGFUTILS_TRACK_FILES': '2'})
        assert res.returncode == 0

        # Check the expected raster filename is reported.
        fn = 'rasterisation-img0.png'
        assert res.stderr.strip() == 'w:' + fn

        self.cleanup()


    def test_rasterisation_file(self):
        """File tracking to file with rasterised image..."""
        # Run the script.
        tfn = os.path.join(dirname, 'tracking.test.results')
        res = build_figure(dirname, 'rasterisation.py', {'PGFUTILS_TRACK_FILES': tfn})
        assert res.returncode == 0

        # Check the expected raster filename is reported.
        fn = 'rasterisation-img0.png'
        with open(tfn, 'r') as f:
            assert f.read().strip() == 'w:' + fn

        self.cleanup()


    def test_loadtxt_stdout(self):
        """File tracking to stdout with loadtxt dependency..."""
        # Run the script.
        res = build_figure(dirname, 'dependency_loadtxt.py', {'PGFUTILS_TRACK_FILES': '1'})
        assert res.returncode == 0

        # Check the expected dependency filename is reported.
        fn = 'scatter.csv'
        assert res.stdout.strip() == 'r:' + fn

        self.cleanup()


    def test_loadtxt_stderr(self):
        """File tracking to stderr with loadtxt dependency..."""
        # Run the script.
        res = build_figure(dirname, 'dependency_loadtxt.py', {'PGFUTILS_TRACK_FILES': '2'})
        assert res.returncode == 0

        # Check the expected dependency filename is reported.
        fn = 'scatter.csv'
        assert res.stderr.strip() == 'r:' + fn

        self.cleanup()


    def test_loadtxt_file(self):
        """File tracking to file with loadtxt dependency..."""
        # Run the script.
        tfn = os.path.join(dirname, 'tracking.test.results')
        res = build_figure(dirname, 'dependency_loadtxt.py', {'PGFUTILS_TRACK_FILES': tfn})
        assert res.returncode == 0

        # Check the expected dependency filename is reported.
        fn = 'scatter.csv'
        with open(tfn, 'r') as f:
            assert f.read().strip() == 'r:' + fn

        self.cleanup()


    def test_load_stdout(self):
        """File tracking to stdout with NumPy format dependency..."""
        # Run the script.
        res = build_figure(dirname, 'dependency_npy.py', {'PGFUTILS_TRACK_FILES': '1'})
        assert res.returncode == 0

        # Check the expected dependency filename is reported.
        fn = 'noise.npy'
        assert res.stdout.strip() == 'r:' + fn

        self.cleanup()


    def test_load_stderr(self):
        """File tracking to stderr with NumPy format dependency..."""
        # Run the script.
        res = build_figure(dirname, 'dependency_npy.py', {'PGFUTILS_TRACK_FILES': '2'})
        assert res.returncode == 0

        # Check the expected dependency filename is reported.
        fn = 'noise.npy'
        assert res.stderr.strip() == 'r:' + fn

        self.cleanup()


    def test_load_file(self):
        """File tracking to file with NumPy format dependency..."""
        # Run the script.
        tfn = os.path.join(dirname, 'tracking.test.results')
        res = build_figure(dirname, 'dependency_npy.py', {'PGFUTILS_TRACK_FILES': tfn})
        assert res.returncode == 0

        # Check the expected dependency filename is reported.
        fn = 'noise.npy'
        with open(tfn, 'r') as f:
            assert f.read().strip() == 'r:' + fn

        self.cleanup()


    def test_multi_stdout(self):
        """File tracking to stdout with multiple dependencies and rasterisation..."""
        # Run the script.
        res = build_figure(dirname, 'multi.py', {'PGFUTILS_TRACK_FILES': '1'})
        assert res.returncode == 0

        # Check the results are as expected.
        expected = {
            'r:noise.npy',
            'r:scatter.csv',
            'w:multi-img0.png',
            'w:multi-img1.png',
        }
        actual = set(res.stdout.strip().splitlines())
        assert actual == expected

        self.cleanup()


    def test_multi_stderr(self):
        """File tracking to stderr with multiple dependencies and rasterisation..."""
        # Run the script.
        res = build_figure(dirname, 'multi.py', {'PGFUTILS_TRACK_FILES': '2'})
        assert res.returncode == 0

        # Check the results are as expected.
        expected = {
            'r:noise.npy',
            'r:scatter.csv',
            'w:multi-img0.png',
            'w:multi-img1.png',
        }
        actual = set(res.stderr.strip().splitlines())
        assert actual == expected

        self.cleanup()


    def test_multi_file(self):
        """File tracking to file with multiple dependencies and rasterisation..."""
        # Run the script.
        tfn = os.path.join(dirname, 'tracking.test.results')
        res = build_figure(dirname, 'multi.py', {'PGFUTILS_TRACK_FILES': tfn})
        assert res.returncode == 0

        # Check the results are as expected.
        expected = {
            'r:noise.npy',
            'r:scatter.csv',
            'w:multi-img0.png',
            'w:multi-img1.png',
        }
        with open(tfn, 'r') as f:
            actual = set(f.read().strip().splitlines())
        assert actual == expected

        self.cleanup()


    def test_ignore_non_image_binary(self):
        """File tracking ignores non-image binary written files..."""
        # Run the script.
        res = build_figure(dirname, 'simple_binary_nonimage.py', {'PGFUTILS_TRACK_FILES': '1'})
        assert res.returncode == 0, "Running tests/tracking_scripts/simple_binary_nonimage.py failed."
        assert os.path.exists("tests/tracking_scripts/test.npy"), "Test output not written."
        assert len(res.stdout.strip()) == 0, "Tracking output was not empty."
        self.cleanup()
        os.unlink("tests/tracking_scripts/test.npy")


    def test_ignore_non_binary(self):
        """File tracking ignores non-binary written files..."""
        # Run the script.
        res = build_figure(dirname, 'simple_nonbinary.py', {'PGFUTILS_TRACK_FILES': '1'})
        assert res.returncode == 0, "Running tests/tracking_scripts/simple_nonbinary.py failed."
        assert os.path.exists("tests/tracking_scripts/test.txt"), "Test output not written."
        assert len(res.stdout.strip()) == 0, "Tracking output was not empty."
        self.cleanup()
        os.unlink("tests/tracking_scripts/test.txt")


    def test_nonfile_opener(self):
        """File tracking ignores openers that don't return file objects..."""
        res = build_figure(dirname, 'simple_nonfile.py', {'PGFUTILS_TRACK_FILES': '1'})
        assert res.returncode == 0, "Running tests/tracking_scripts/simple_nonfile.py failed."
        assert os.path.exists("tests/tracking_scripts/test_nonfile.png"), "Test output not written."
        assert len(res.stdout.strip()) == 0, "Tracking output was not empty."
        self.cleanup()


    def test_fdopen(self):
        """File tracking ignores file objects from os.fdopen..."""
        res = build_figure(dirname, 'simple_fdopen.py', {'PGFUTILS_TRACK_FILES': '1'})
        assert res.returncode == 0, "Running tests/tracking_scripts/simple_fdopen.py failed."
        assert os.path.exists("tests/tracking_scripts/test_fdopen.png"), "Test output not written."
        assert len(res.stdout.strip()) == 0, "Tracking output was not empty."
        self.cleanup()


    def test_nonproject(self):
        """File tracking ignores files written outside top-level directory..."""
        res = build_figure(dirname, 'simple_nonproject.py', {'PGFUTILS_TRACK_FILES': '1'})
        assert res.returncode == 0, "Running tests/tracking_scripts/simple_nonproject.py failed."
        tfn = os.path.join(tempfile.gettempdir(), "test_nonproject.png")
        assert os.path.exists(tfn), "Test output not written."
        assert len(res.stdout.strip()) == 0, "Tracking output was not empty."
        self.cleanup()
        os.unlink(tfn)
