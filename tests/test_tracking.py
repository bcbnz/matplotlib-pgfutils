# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from pathlib import Path
import tempfile

import pytest

import pgfutils

from .utils import build_pypgf

srcdir = Path(__file__).parent / "sources" / "tracking"


class TestTrackingClass:
    def test_simple_stdout(self):
        """File tracking to stdout with no dependencies or rasterisation..."""
        # Run the script and check no files were reported.
        env = {"PGFUTILS_TRACK_FILES": "1"}
        with build_pypgf(srcdir, "simple.py", env) as res:
            assert res.returncode == 0
            assert len(res.stdout.strip()) == 0

    def test_simple_stderr(self):
        """File tracking to stderr with no dependencies or rasterisation..."""
        # Run the script and check no files were reported.
        env = {"PGFUTILS_TRACK_FILES": "2"}
        with build_pypgf(srcdir, "simple.py", env) as res:
            assert res.returncode == 0
            assert len(res.stderr.strip()) == 0

    def test_simple_file(self):
        """File tracking to file with no dependencies or rasterisation..."""
        # Run the script and check no files were reported.
        tfn = srcdir / "tracking.test.results"
        env = {"PGFUTILS_TRACK_FILES": str(tfn)}
        with build_pypgf(srcdir, "simple.py", env) as res:
            assert res.returncode == 0
            stat = tfn.stat()
            assert stat.st_size == 0

    def test_rasterisation_stdout(self):
        """File tracking to stdout with rasterised image..."""
        # Run the script.
        env = {"PGFUTILS_TRACK_FILES": "1"}
        with build_pypgf(srcdir, "rasterisation.py", env) as res:
            assert res.returncode == 0

            # Check the expected raster filename is reported.
            fn = "rasterisation-img0.png"
            assert res.stdout.strip() == "w:" + fn

    def test_rasterisation_stderr(self):
        """File tracking to stderr with rasterised image..."""
        # Run the script.
        env = {"PGFUTILS_TRACK_FILES": "2"}
        with build_pypgf(srcdir, "rasterisation.py", env) as res:
            assert res.returncode == 0

            # Check the expected raster filename is reported.
            fn = "rasterisation-img0.png"
            assert res.stderr.strip() == "w:" + fn

    def test_rasterisation_file(self):
        """File tracking to file with rasterised image..."""
        # Run the script.
        tfn = srcdir / "tracking.test.results"
        env = {"PGFUTILS_TRACK_FILES": str(tfn)}
        with build_pypgf(srcdir, "rasterisation.py", env) as res:
            assert res.returncode == 0

            # Check the expected raster filename is reported.
            fn = "rasterisation-img0.png"
            with open(tfn, "r") as f:
                assert f.read().strip() == "w:" + fn

    def test_loadtxt_stdout(self):
        """File tracking to stdout with loadtxt dependency..."""
        # Run the script.
        env = {"PGFUTILS_TRACK_FILES": "1"}
        with build_pypgf(srcdir, "dependency_loadtxt.py", env) as res:
            assert res.returncode == 0

            # Check the expected dependency filename is reported.
            fn = "scatter.csv"
            assert res.stdout.strip() == "r:" + fn

    def test_loadtxt_stderr(self):
        """File tracking to stderr with loadtxt dependency..."""
        # Run the script.
        env = {"PGFUTILS_TRACK_FILES": "2"}
        with build_pypgf(srcdir, "dependency_loadtxt.py", env) as res:
            assert res.returncode == 0

            # Check the expected dependency filename is reported.
            fn = "scatter.csv"
            assert res.stderr.strip() == "r:" + fn

    def test_loadtxt_file(self):
        """File tracking to file with loadtxt dependency..."""
        # Run the script.
        tfn = srcdir / "tracking.test.results"
        env = {"PGFUTILS_TRACK_FILES": str(tfn)}
        with build_pypgf(srcdir, "dependency_loadtxt.py", env) as res:
            assert res.returncode == 0

            # Check the expected dependency filename is reported.
            fn = "scatter.csv"
            with open(tfn, "r") as f:
                assert f.read().strip() == "r:" + fn

    def test_pathlib_stdout(self):
        """File tracking to stdout with pathlib dependency..."""
        # Run the script.
        env = {"PGFUTILS_TRACK_FILES": "1"}
        with build_pypgf(srcdir, "dependency_pathlib.py", env) as res:
            assert res.returncode == 0

            # Check the expected dependency filename is reported.
            fn = "scatter.csv"
            assert res.stdout.strip() == "r:" + fn

    def test_pathlib_stderr(self):
        """File tracking to stderr with pathlib dependency..."""
        # Run the script.
        env = {"PGFUTILS_TRACK_FILES": "2"}
        with build_pypgf(srcdir, "dependency_pathlib.py", env) as res:
            assert res.returncode == 0

            # Check the expected dependency filename is reported.
            fn = "scatter.csv"
            assert res.stderr.strip() == "r:" + fn

    def test_pathlib_file(self):
        """File tracking to file with pathlib dependency..."""
        # Run the script.
        tfn = srcdir / "tracking.test.results"
        env = {"PGFUTILS_TRACK_FILES": str(tfn)}
        with build_pypgf(srcdir, "dependency_pathlib.py", env) as res:
            assert res.returncode == 0

            # Check the expected dependency filename is reported.
            fn = "scatter.csv"
            with open(tfn, "r") as f:
                assert f.read().strip() == "r:" + fn

    def test_load_stdout(self):
        """File tracking to stdout with NumPy format dependency..."""
        # Run the script.
        env = {"PGFUTILS_TRACK_FILES": "1"}
        with build_pypgf(srcdir, "dependency_npy.py", env) as res:
            assert res.returncode == 0

            # Check the expected dependency filename is reported.
            fn = "noise.npy"
            assert res.stdout.strip() == "r:" + fn

    def test_load_stderr(self):
        """File tracking to stderr with NumPy format dependency..."""
        # Run the script.
        env = {"PGFUTILS_TRACK_FILES": "2"}
        with build_pypgf(srcdir, "dependency_npy.py", env) as res:
            assert res.returncode == 0

            # Check the expected dependency filename is reported.
            fn = "noise.npy"
            assert res.stderr.strip() == "r:" + fn

    def test_load_file(self):
        """File tracking to file with NumPy format dependency..."""
        # Run the script.
        tfn = srcdir / "tracking.test.results"
        env = {"PGFUTILS_TRACK_FILES": str(tfn)}
        with build_pypgf(srcdir, "dependency_npy.py", env) as res:
            assert res.returncode == 0

            # Check the expected dependency filename is reported.
            fn = "noise.npy"
            with open(tfn, "r") as f:
                assert f.read().strip() == "r:" + fn

    def test_multi_stdout(self):
        """File tracking to stdout with multiple dependencies and rasterisation..."""
        # Run the script.
        env = {"PGFUTILS_TRACK_FILES": "1"}
        with build_pypgf(srcdir, "multi.py", env) as res:
            assert res.returncode == 0

            # Check the results are as expected.
            expected = {
                "r:noise.npy",
                "r:scatter.csv",
                "r:extra.file",
                "w:multi-img0.png",
                "w:multi-img1.png",
            }
            actual = set(res.stdout.strip().splitlines())
            assert actual == expected

    def test_multi_stderr(self):
        """File tracking to stderr with multiple dependencies and rasterisation..."""
        # Run the script.
        env = {"PGFUTILS_TRACK_FILES": "2"}
        with build_pypgf(srcdir, "multi.py", env) as res:
            assert res.returncode == 0

            # Check the results are as expected.
            expected = {
                "r:noise.npy",
                "r:scatter.csv",
                "r:extra.file",
                "w:multi-img0.png",
                "w:multi-img1.png",
            }
            actual = set(res.stderr.strip().splitlines())
            assert actual == expected

    def test_multi_file(self):
        """File tracking to file with multiple dependencies and rasterisation..."""
        # Run the script.
        tfn = srcdir / "tracking.test.results"
        env = {"PGFUTILS_TRACK_FILES": str(tfn)}
        with build_pypgf(srcdir, "multi.py", env) as res:
            assert res.returncode == 0

            # Check the results are as expected.
            expected = {
                "r:noise.npy",
                "r:scatter.csv",
                "r:extra.file",
                "w:multi-img0.png",
                "w:multi-img1.png",
            }
            with open(tfn, "r") as f:
                actual = set(f.read().strip().splitlines())
            assert actual == expected

    def test_extradirs_stdout(self):
        """File tracking to stdout with extra dependency directories."""
        # Run the script.
        extra_dir = srcdir / "extra_dirs"
        env = {"PGFUTILS_TRACK_FILES": "1"}
        with build_pypgf(extra_dir, "multi.py", env) as res:
            assert res.returncode == 0

            # Check the results are as expected.
            absdir = extra_dir.resolve()
            expected = {
                "r:pgfutils.cfg",
                f"r:{(absdir / '../noise.npy').resolve()}",
                "r:scatter.csv",
                f"r:{(absdir / '../../extra.file').resolve()}",
                "w:multi-img0.png",
                "w:multi-img1.png",
            }
            actual = set(res.stdout.strip().splitlines())
            assert actual == expected

    def test_extradirs_stderr(self):
        """File tracking to stderr with extra dependency directories."""
        # Run the script.
        extra_dir = srcdir / "extra_dirs"
        env = {"PGFUTILS_TRACK_FILES": "2"}
        with build_pypgf(extra_dir, "multi.py", env) as res:
            assert res.returncode == 0

            # Check the results are as expected.
            absdir = extra_dir.resolve()
            expected = {
                "r:pgfutils.cfg",
                f"r:{(absdir / '../noise.npy').resolve()}",
                "r:scatter.csv",
                f"r:{(absdir / '../../extra.file').resolve()}",
                "w:multi-img0.png",
                "w:multi-img1.png",
            }
            actual = set(res.stderr.strip().splitlines())
            assert actual == expected

    def test_extradirs_file(self):
        """File tracking to file with extra dependency directories."""
        # Run the script.
        extra_dir = srcdir / "extra_dirs"
        tfn = srcdir / "tracking.test.results"
        env = {"PGFUTILS_TRACK_FILES": str(tfn)}
        with build_pypgf(extra_dir, "multi.py", env) as res:
            assert res.returncode == 0

            # Check the results are as expected.
            absdir = extra_dir.resolve()
            expected = {
                "r:pgfutils.cfg",
                f"r:{(absdir / '../noise.npy').resolve()}",
                "r:scatter.csv",
                f"r:{(absdir / '../../extra.file').resolve()}",
                "w:multi-img0.png",
                "w:multi-img1.png",
            }
            with open(tfn, "r") as f:
                actual = set(f.read().strip().splitlines())
            assert actual == expected

    def test_ignore_non_image_binary(self):
        """File tracking ignores non-image binary written files..."""
        # Run the script.
        env = {"PGFUTILS_TRACK_FILES": "1"}
        with build_pypgf(srcdir, "simple_binary_nonimage.py", env) as res:
            assert res.returncode == 0, (
                f"Running {srcdir / 'simple_binary_nonimage.py'} failed."
            )

            npfn = srcdir / "test.npy"
            assert npfn.exists(), "Test output not written."
            npfn.unlink()
            assert len(res.stdout.strip()) == 0, "Tracking output was not empty."

    def test_ignore_non_binary(self):
        """File tracking ignores non-binary written files..."""
        # Run the script.
        env = {"PGFUTILS_TRACK_FILES": "1"}
        with build_pypgf(srcdir, "simple_nonbinary.py", env) as res:
            assert res.returncode == 0, (
                f"Running {srcdir / 'simple_nonbinary.py'} failed."
            )

            txtfn = srcdir / "test.txt"
            assert txtfn.exists(), "Test output not written."
            txtfn.unlink()
            assert len(res.stdout.strip()) == 0, "Tracking output was not empty."

    def test_nonfile_opener(self):
        """File tracking ignores openers that don't return file objects..."""
        env = {"PGFUTILS_TRACK_FILES": "1"}
        with build_pypgf(srcdir, "simple_nonfile.py", env) as res:
            assert res.returncode == 0, (
                f"Running {srcdir / 'simple_nonfile.py'} failed."
            )

            pngfn = srcdir / "test_nonfile.png"
            assert pngfn.exists(), "Test output not written."
            pngfn.unlink()
            assert len(res.stdout.strip()) == 0, "Tracking output was not empty."

    def test_fdopen(self):
        """File tracking ignores file objects from os.fdopen..."""
        env = {"PGFUTILS_TRACK_FILES": "1"}
        with build_pypgf(srcdir, "simple_fdopen.py", env) as res:
            assert res.returncode == 0, f"Running {srcdir / 'simple_fdopen.py'} failed."

            pngfn = srcdir / "test_fdopen.png"
            assert pngfn.exists(), "Test output not written."
            pngfn.unlink()
            assert len(res.stdout.strip()) == 0, "Tracking output was not empty."

    def test_nonproject(self):
        """File tracking ignores files written outside top-level directory..."""
        env = {"PGFUTILS_TRACK_FILES": "1"}
        with build_pypgf(srcdir, "simple_nonproject.py", env) as res:
            assert res.returncode == 0, (
                f"Running {srcdir / 'simple_nonproject.py'} failed."
            )

            pngfn = Path(tempfile.gettempdir()) / "test_nonproject.png"
            assert pngfn.exists(), "Test output not written."
            pngfn.unlink()
            assert len(res.stdout.strip()) == 0, "Tracking output was not empty."

    def test_manual_stdout(self):
        """File tracking to stdout with manual dependencies..."""
        env = {"PGFUTILS_TRACK_FILES": "1"}
        tests = {
            "manual_dependency.py": {"r:data.file"},
            "manual_dependencies.py": {"r:data.file", "r:another.file"},
        }
        for script, expected in tests.items():
            # Run the script and check it succeeded.
            with build_pypgf(srcdir, script, env) as res:
                assert res.returncode == 0, f"Running {srcdir / script} failed,"

                # Check the output files are correct.
                actual = set(res.stdout.strip().splitlines())
                assert actual == expected

    def test_manual_stderr(self):
        """File tracking to stderr with manual dependencies..."""
        env = {"PGFUTILS_TRACK_FILES": "2"}
        tests = {
            "manual_dependency.py": {"r:data.file"},
            "manual_dependencies.py": {"r:data.file", "r:another.file"},
        }
        for script, expected in tests.items():
            # Run the script and check it succeeded.
            with build_pypgf(srcdir, script, env) as res:
                assert res.returncode == 0, f"Running {srcdir / script} failed,"

                # Check the output files are correct.
                actual = set(res.stderr.strip().splitlines())
                assert actual == expected

    def test_manual_file(self):
        """File tracking to file with manual dependencies..."""
        tfn = srcdir / "tracking.test.results"
        env = {"PGFUTILS_TRACK_FILES": str(tfn)}
        tests = {
            "manual_dependency.py": {"r:data.file"},
            "manual_dependencies.py": {"r:data.file", "r:another.file"},
        }
        for script, expected in tests.items():
            # Run the script and check it succeeded.
            with build_pypgf(srcdir, script, env) as res:
                assert res.returncode == 0, f"Running {srcdir / script} failed,"

                # Check the expected dependencies are reported.
                with open(tfn, "r") as f:
                    actual = set(f.read().splitlines())
                assert actual == expected

    def test_extra_trackers_unknown(self):
        """File trackers raises error if unknown extra_tracking option given..."""
        with pytest.raises(ValueError):
            pgfutils._install_extra_file_trackers(["unknown"])

        try:
            import netCDF4  # noqa: F401
        except ImportError:
            pass
        else:
            with pytest.raises(ValueError):
                pgfutils._install_extra_file_trackers(["netCDF4", "unknown"])

    def test_netcdf4_setup(self):
        """File tracking with netCDF4 library enabled in setup()..."""
        pytest.importorskip("netCDF4", reason="netCDF4 not installed; cannot test.")

        env = {"PGFUTILS_TRACK_FILES": "1"}
        with build_pypgf(srcdir, "netcdf4_in_setup.py", env) as res:
            assert res.returncode == 0, (
                f"Running {srcdir / 'netcdf4_in_setup.py'} failed."
            )
            actual = set(res.stdout.strip().splitlines())
            expected = {
                "r:netcdf4/sine.nc",
            }
            assert actual == expected

    def test_netcdf4_cfg(self):
        """File tracking with netCDF4 library enabled in pgfutils.cfg..."""
        pytest.importorskip("netCDF4", reason="netCDF4 not installed; cannot test.")

        env = {"PGFUTILS_TRACK_FILES": "1"}
        with build_pypgf(srcdir / "netcdf4", "netcdf4.py", env) as res:
            assert res.returncode == 0, (
                f"Running {srcdir / 'netcdf4' / 'netcdf4.py'} failed."
            )
            actual = set(res.stdout.strip().splitlines())
            expected = {"r:sine.nc", "r:pgfutils.cfg"}
            assert actual == expected

    def test_netcdf4_ignores_written(self):
        """File tracking ignores files written by netCDF4..."""
        pytest.importorskip("netCDF4", reason="netCDF4 not installed; cannot test.")

        env = {"PGFUTILS_TRACK_FILES": "1"}
        with build_pypgf(srcdir, "netcdf4_write.py", env) as res:
            assert res.returncode == 0, f"Running {srcdir / 'netcdf4_write.py'} failed."
            ncfn = srcdir / "test_output.nc"
            assert ncfn.exists(), "Output not written."
            ncfn.unlink()
            actual = set(res.stdout.strip().splitlines())
            assert not actual

    def test_netcdf4_multi_explicit(self):
        """File tracking works with netCDF4 MFDataset (explicit list)..."""
        pytest.importorskip("netCDF4", reason="netCDF4 not installed; cannot test.")

        env = {"PGFUTILS_TRACK_FILES": "1"}
        with build_pypgf(srcdir / "netcdf4", "netcdf4_multi_explicit.py", env) as res:
            assert res.returncode == 0, (
                f"Running {srcdir / 'netcdf4' / 'netcdf4_multi_explicit.py'} failed."
            )
            actual = set(res.stdout.strip().splitlines())
            expected = {
                "r:mftest0.nc",
                "r:mftest1.nc",
                "r:mftest2.nc",
                "r:pgfutils.cfg",
            }
            assert actual == expected

    def test_netcdf4_multi_glob(self):
        """File tracking works with netCDF4 MFDataset (filename glob)..."""
        pytest.importorskip("netCDF4", reason="netCDF4 not installed; cannot test.")

        env = {"PGFUTILS_TRACK_FILES": "1"}
        with build_pypgf(srcdir / "netcdf4", "netcdf4_multi_glob.py", env) as res:
            assert res.returncode == 0, (
                f"Running {srcdir / 'netcdf4' / 'netcdf4_multi_glob.py'} failed."
            )
            actual = set(res.stdout.strip().splitlines())
            expected = {
                "r:mftest0.nc",
                "r:mftest1.nc",
                "r:mftest2.nc",
                "r:pgfutils.cfg",
            }
            assert actual == expected

    def test_import_tracking_pythonpath(self):
        """File tracking handles imports from paths.pythonpath..."""
        libdir = srcdir.resolve() / "imports" / "lib"
        env = {"PGFUTILS_TRACK_FILES": "1"}
        dir = srcdir / "imports" / "cfg_pythonpath"
        with build_pypgf(dir, "figure.py", env) as res:
            assert res.returncode == 0, f"Running {dir / 'figure.py'} failed."
            actual = set(res.stdout.strip().splitlines())
            expected = {"r:pgfutils.cfg", f"r:{libdir / 'custom_lib.py'}"}
            assert actual == expected

    def test_import_tracking_extra_imports(self):
        """File tracking handles imports from paths.extra_imports..."""
        libdir = srcdir.resolve() / "imports" / "lib"
        env = {"PGFUTILS_TRACK_FILES": "1", "PYTHONPATH": str(libdir)}
        dir = srcdir / "imports" / "cfg_extra"
        with build_pypgf(dir, "figure.py", env) as res:
            assert res.returncode == 0, f"Running {dir / 'figure.py'} failed."
            actual = set(res.stdout.strip().splitlines())
            expected = {"r:pgfutils.cfg", f"r:{libdir / 'custom_lib.py'}"}
            assert actual == expected

    def test_track_enabled_config(self):
        """File tracking can be enabled through configured environment variables..."""
        # Run the script.
        with build_pypgf(srcdir / "config_enabled", "config_enabled.py") as res:
            assert res.returncode == 0, (
                f"Running {srcdir / 'config_enabled' / 'config_enabled.py'} failed."
            )

            # Check the results are as expected.
            expected = {
                "r:pgfutils.cfg",
                "r:noise.npy",
                "r:scatter.csv",
                "r:extra.file",
                "w:config_enabled-img0.png",
                "w:config_enabled-img1.png",
            }
            actual = set(res.stdout.strip().splitlines())
            assert actual == expected
