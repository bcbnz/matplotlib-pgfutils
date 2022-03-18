import pgfutils
import pytest

import os
import os.path
from .utils import build_figure, build_tex
import tempfile

dirname = os.path.join(os.path.normpath(os.path.dirname(__file__)), "sources/tracking")


class TestTrackingClass:
    def cleanup(self):
        for root, dirs, files in os.walk(dirname):
            for fn in files:
                base, ext = os.path.splitext(fn)
                if ext in {'.pypgf', '.png'}:
                    os.unlink(os.path.join(root, fn))
                if fn == 'tracking.test.results':
                    os.unlink(os.path.join(root, fn))
                if fn == 'test_output.nc':
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


    def test_pathlib_stdout(self):
        """File tracking to stdout with pathlib dependency..."""
        # Run the script.
        res = build_figure(dirname, 'dependency_pathlib.py', {'PGFUTILS_TRACK_FILES': '1'})
        assert res.returncode == 0

        # Check the expected dependency filename is reported.
        fn = 'scatter.csv'
        assert res.stdout.strip() == 'r:' + fn

        self.cleanup()


    def test_pathlib_stderr(self):
        """File tracking to stderr with pathlib dependency..."""
        # Run the script.
        res = build_figure(dirname, 'dependency_pathlib.py', {'PGFUTILS_TRACK_FILES': '2'})
        assert res.returncode == 0

        # Check the expected dependency filename is reported.
        fn = 'scatter.csv'
        assert res.stderr.strip() == 'r:' + fn

        self.cleanup()


    def test_pathlib_file(self):
        """File tracking to file with pathlib dependency..."""
        # Run the script.
        tfn = os.path.join(dirname, 'tracking.test.results')
        res = build_figure(dirname, 'dependency_pathlib.py', {'PGFUTILS_TRACK_FILES': tfn})
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
            'r:extra.file',
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
            'r:extra.file',
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
            'r:extra.file',
            'w:multi-img0.png',
            'w:multi-img1.png',
        }
        with open(tfn, 'r') as f:
            actual = set(f.read().strip().splitlines())
        assert actual == expected

        self.cleanup()


    def test_extradirs_stdout(self):
        """File tracking to stdout with extra dependency directories."""
        # Run the script.
        extra_dir = os.path.join(dirname, "extra_dirs")
        res = build_figure(extra_dir, 'multi.py', {'PGFUTILS_TRACK_FILES': '1'})
        assert res.returncode == 0

        # Check the results are as expected.
        absdir = os.path.abspath(dirname)
        expected = {
            'r:pgfutils.cfg',
            'r:{0:s}'.format(os.path.join(absdir, 'noise.npy')),
            'r:scatter.csv',
            'r:../../extra.file',
            'w:multi-img0.png',
            'w:multi-img1.png',
        }
        actual = set(res.stdout.strip().splitlines())
        assert actual == expected

        self.cleanup()


    def test_extradirs_stderr(self):
        """File tracking to stderr with extra dependency directories."""
        # Run the script.
        extra_dir = os.path.join(dirname, "extra_dirs")
        res = build_figure(extra_dir, 'multi.py', {'PGFUTILS_TRACK_FILES': '2'})
        assert res.returncode == 0

        # Check the results are as expected.
        absdir = os.path.abspath(dirname)
        expected = {
            'r:pgfutils.cfg',
            'r:{0:s}'.format(os.path.join(absdir, 'noise.npy')),
            'r:scatter.csv',
            'r:../../extra.file',
            'w:multi-img0.png',
            'w:multi-img1.png',
        }
        actual = set(res.stderr.strip().splitlines())
        assert actual == expected

        self.cleanup()


    def test_extradirs_file(self):
        """File tracking to file with extra dependency directories."""
        # Run the script.
        extra_dir = os.path.join(dirname, "extra_dirs")
        tfn = os.path.join(extra_dir, 'tracking.test.results')
        res = build_figure(extra_dir, 'multi.py', {'PGFUTILS_TRACK_FILES': tfn})
        assert res.returncode == 0

        # Check the results are as expected.
        absdir = os.path.abspath(dirname)
        expected = {
            'r:pgfutils.cfg',
            'r:{0:s}'.format(os.path.join(absdir, 'noise.npy')),
            'r:scatter.csv',
            'r:../../extra.file',
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
        assert res.returncode == 0, "Running tests/sources/tracking/simple_binary_nonimage.py failed."
        assert os.path.exists("tests/sources/tracking/test.npy"), "Test output not written."
        assert len(res.stdout.strip()) == 0, "Tracking output was not empty."
        self.cleanup()
        os.unlink("tests/sources/tracking/test.npy")


    def test_ignore_non_binary(self):
        """File tracking ignores non-binary written files..."""
        # Run the script.
        res = build_figure(dirname, 'simple_nonbinary.py', {'PGFUTILS_TRACK_FILES': '1'})
        assert res.returncode == 0, "Running tests/sources/tracking/simple_nonbinary.py failed."
        assert os.path.exists("tests/sources/tracking/test.txt"), "Test output not written."
        assert len(res.stdout.strip()) == 0, "Tracking output was not empty."
        self.cleanup()
        os.unlink("tests/sources/tracking/test.txt")


    def test_nonfile_opener(self):
        """File tracking ignores openers that don't return file objects..."""
        res = build_figure(dirname, 'simple_nonfile.py', {'PGFUTILS_TRACK_FILES': '1'})
        assert res.returncode == 0, "Running tests/sources/tracking/simple_nonfile.py failed."
        assert os.path.exists("tests/sources/tracking/test_nonfile.png"), "Test output not written."
        assert len(res.stdout.strip()) == 0, "Tracking output was not empty."
        self.cleanup()


    def test_fdopen(self):
        """File tracking ignores file objects from os.fdopen..."""
        res = build_figure(dirname, 'simple_fdopen.py', {'PGFUTILS_TRACK_FILES': '1'})
        assert res.returncode == 0, "Running tests/sources/tracking/simple_fdopen.py failed."
        assert os.path.exists("tests/sources/tracking/test_fdopen.png"), "Test output not written."
        assert len(res.stdout.strip()) == 0, "Tracking output was not empty."
        self.cleanup()


    def test_nonproject(self):
        """File tracking ignores files written outside top-level directory..."""
        res = build_figure(dirname, 'simple_nonproject.py', {'PGFUTILS_TRACK_FILES': '1'})
        assert res.returncode == 0, "Running tests/sources/tracking/simple_nonproject.py failed."
        tfn = os.path.join(tempfile.gettempdir(), "test_nonproject.png")
        assert os.path.exists(tfn), "Test output not written."
        assert len(res.stdout.strip()) == 0, "Tracking output was not empty."
        self.cleanup()
        os.unlink(tfn)


    def test_manual_stdout(self):
        """File tracking to stdout with manual dependencies..."""
        tests = {
            "manual_dependency.py": {"r:data.file"},
            "manual_dependencies.py": {"r:data.file", "r:another.file"},
        }
        for script, expected in tests.items():
            # Run the script and check it succeeded.
            res = build_figure(dirname, script, {'PGFUTILS_TRACK_FILES': '1'})
            assert res.returncode == 0

            # Check the output files are correct.
            actual = set(res.stdout.strip().splitlines())
            assert actual == expected
            self.cleanup()


    def test_manual_stderr(self):
        """File tracking to stderr with manual dependencies..."""
        tests = {
            "manual_dependency.py": {"r:data.file"},
            "manual_dependencies.py": {"r:data.file", "r:another.file"},
        }
        for script, expected in tests.items():
            # Run the script and check it succeeded.
            res = build_figure(dirname, script, {'PGFUTILS_TRACK_FILES': '2'})
            assert res.returncode == 0

            # Check the output files are correct.
            actual = set(res.stderr.strip().splitlines())
            assert actual == expected
            self.cleanup()


    def test_manual_file(self):
        """File tracking to file with manual dependencies..."""
        tfn = os.path.join(dirname, 'tracking.test.results')
        tests = {
            "manual_dependency.py": {"r:data.file"},
            "manual_dependencies.py": {"r:data.file", "r:another.file"},
        }
        for script, expected in tests.items():
            # Run the script and check it succeeded.
            res = build_figure(dirname, script, {'PGFUTILS_TRACK_FILES': tfn})
            assert res.returncode == 0

            # Check the expected dependencies are reported.
            with open(tfn, 'r') as f:
                actual = set(f.read().splitlines())
            assert actual == expected
            self.cleanup()


    def test_extra_trackers_unknown(self):
        """File trackers raises error if unknown extra_tracking option given..."""
        with pytest.raises(ValueError):
            pgfutils._install_extra_file_trackers(["unknown"])
        try:
            import netCDF4
        except ImportError:
            pass
        else:
            with pytest.raises(ValueError):
                pgfutils._install_extra_file_trackers(["netCDF4", "unknown"])


    def test_netcdf4_setup(self):
        """File tracking with netCDF4 library enabled in setup()..."""
        try:
            import netCDF4
        except ImportError:
            pytest.skip("netCDF4 not installed; cannot test.")

        res = build_figure(dirname, "netcdf4_in_setup.py", {"PGFUTILS_TRACK_FILES": "1"})
        assert res.returncode == 0
        actual = set(res.stdout.strip().splitlines())
        expected = {"r:netcdf4/sine.nc",}
        assert actual == expected
        self.cleanup()


    def test_netcdf4_cfg(self):
        """File tracking with netCDF4 library enabled in pgfutils.cfg..."""
        try:
            import netCDF4
        except ImportError:
            pytest.skip("netCDF4 not installed; cannot test.")

        res = build_figure(os.path.join(dirname, "netcdf4"), "netcdf4.py", {"PGFUTILS_TRACK_FILES": "1"})
        assert res.returncode == 0
        actual = set(res.stdout.strip().splitlines())
        expected = {"r:sine.nc", "r:pgfutils.cfg"}
        assert actual == expected
        self.cleanup()


    def test_netcdf4_ignores_written(self):
        """File tracking ignores files written by netCDF4..."""
        try:
            import netCDF4
        except ImportError:
            pytest.skip("netCDF4 not installed; cannot test.")

        res = build_figure(dirname, "netcdf4_write.py", {"PGFUTILS_TRACK_FILES": "1"})
        assert res.returncode == 0
        actual = set(res.stdout.strip().splitlines())
        assert not actual
        self.cleanup()


    def test_netcdf4_multi_explicit(self):
        """File tracking works with netCDF4 MFDataset (explicit list)..."""
        try:
            import netCDF4
        except ImportError:
            pytest.skip("netCDF4 not installed; cannot test.")

        res = build_figure(os.path.join(dirname, "netcdf4"), "netcdf4_multi_explicit.py",
                {"PGFUTILS_TRACK_FILES": "1"})
        assert res.returncode == 0
        actual = set(res.stdout.strip().splitlines())
        expected = {"r:mftest0.nc", "r:mftest1.nc", "r:mftest2.nc", "r:pgfutils.cfg"}
        assert actual == expected
        self.cleanup()


    def test_netcdf4_multi_glob(self):
        """File tracking works with netCDF4 MFDataset (filename glob)..."""
        try:
            import netCDF4
        except ImportError:
            pytest.skip("netCDF4 not installed; cannot test.")

        res = build_figure(os.path.join(dirname, "netcdf4"), "netcdf4_multi_glob.py",
                {"PGFUTILS_TRACK_FILES": "1"})
        assert res.returncode == 0
        actual = set(res.stdout.strip().splitlines())
        expected = {"r:mftest0.nc", "r:mftest1.nc", "r:mftest2.nc", "r:pgfutils.cfg"}
        assert actual == expected
        self.cleanup()


    def test_import_tracking_pythonpath(self):
        """File tracking handles imports from paths.pythonpath..."""
        libdir = os.path.abspath(os.path.join(dirname, "imports", "lib"))
        res = build_figure(
            os.path.join(dirname, "imports", "cfg_pythonpath"),
            "figure.py",
            {"PGFUTILS_TRACK_FILES": "1"}
        )
        assert res.returncode == 0
        actual = set(res.stdout.strip().splitlines())
        expected = {
            "r:pgfutils.cfg",
            "r:{}".format(os.path.join(libdir, "custom_lib.py"))
        }
        assert actual == expected
        self.cleanup()


    def test_import_tracking_extra_imports(self):
        """File tracking handles imports from paths.extra_imports..."""
        libdir = os.path.abspath(os.path.join(dirname, "imports", "lib"))
        res = build_figure(
            os.path.join(dirname, "imports", "cfg_extra"),
            "figure.py",
            {"PGFUTILS_TRACK_FILES": "1", "PYTHONPATH": libdir}
        )
        assert res.returncode == 0
        actual = set(res.stdout.strip().splitlines())
        expected = {
            "r:pgfutils.cfg",
            "r:{}".format(os.path.join(libdir, "custom_lib.py"))
        }
        assert actual == expected
        self.cleanup()


    def test_track_enabled_config(self):
        """File tracking can be enabled through configured environment variables..."""
        # Run the script.
        res = build_figure(os.path.join(dirname, "config_enabled"), 'config_enabled.py')
        assert res.returncode == 0

        # Check the results are as expected.
        expected = {
            'r:pgfutils.cfg',
            'r:noise.npy',
            'r:scatter.csv',
            'r:extra.file',
            'w:config_enabled-img0.png',
            'w:config_enabled-img1.png',
        }
        actual = set(res.stdout.strip().splitlines())
        assert actual == expected
        self.cleanup()
