# Copyright 2018, 2019, 2020, 2021, 2022 Blair Bonnett
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""Utilities for generating PGF plots from matplotlib.

From version 1.2, matplotlib has included a PGF backend. This exports figures
as drawing commands for the PGF drawing package for LaTeX, allowing LaTeX to
typeset the image. This module provides some utilities to simplify creating PGF
figures from scripts (so they can be processed via Makefiles) in order to get
consistent-looking plots.

"""

__version__ = "1.7.0"

# We don't import Matplotlib here as this brings in NumPy. In turn, NumPy
# caches a reference to the io.open() method as part of its data loading
# functions. This means we can't (reliably) wrap all loading functions if we're
# asked to track opened files. Instead, the tracking is installed in
# setup_figure() before the first import of Matplotlib (assuming the user
# doesn't use our internal functions). Python's caching of imported modules
# means there should be minimal impact from importing Matplotlib separately in
# different functions.

import configparser
import importlib.abc
import inspect
import io
import os
import os.path
import pathlib
import re
import string
import sys


class DimensionError(Exception):
    """A configuration entry could not be converted to a dimension."""
    pass


class ColorError(Exception):
    """A configuration entry could not be converted to a color."""
    pass


class PgfutilsParser(configparser.ConfigParser):
    """Custom configuration parser with Matplotlib dimension and color support.

    """
    # Regular expression to parse a dimension into size and (optional) unit.
    _dimre = re.compile(r"^\s*(?P<size>\d+(?:\.\d*)?)\s*(?P<unit>.+?)?\s*$")

    # Conversion factors (divisors) to go from the given unit to inches.
    _dimconv = {
        'cm': 2.54,
        'centimetre': 2.54,
        'centimeter': 2.54,
        'centimetres': 2.54,
        'centimeters': 2.54,
        'mm': 25.4,
        'millimetre': 25.4,
        'millimeter': 25.4,
        'millimetres': 25.4,
        'millimeters': 25.4,
        'in': 1,
        'inch': 1,
        'inches': 1,
        'pt': 72.27,  # Printers points, not the 1/72 Postscript/PDF points.
        'point': 72.27,
        'points': 72.27,
    }


    def read(self, filename, encoding=None):
        """Read configuration options from a file.

        This is an extension of the standard ConfigParser.read() method to
        reject unknown options. This provides an early indication to the user
        that they have configured something incorrectly, rather than continuing
        and having their plot generated differently to how they intended it.

        """
        def get_options():
            options = set()
            for sect, opts in self._sections.items():
                if sect == 'rcParams':
                    continue
                options.update('{}.{}'.format(sect, opt) for opt in opts.keys())
            return options

        # Get the options before and after reading.
        before = get_options()
        result = super().read(filename, encoding)
        after = get_options()

        # If there's a difference, thats an error.
        diff = after.difference(before)
        if diff:
            if len(diff) == 1:
                raise KeyError("{}: unknown option {}".format(filename, diff.pop()))
            raise KeyError("{}: unknown options {}".format(filename, ', '.join(diff)))

        # Otherwise we're OK to continue.
        return result


    def read_kwargs(self, **kwargs):
        """Read configuration options from keyword arguments.

        """
        # Dictionary of values to load.
        d = {}

        # Option -> section lookup table.
        lookup = {}

        # Go through all existing options.
        for section, options in self._sections.items():
            # Can't specify rcParams through kwargs.
            if section == 'rcParams':
                continue

            # Add to our tables.
            d[section] = {}
            for option in options.keys():
                lookup[option] = section

        # Go through all given arguments.
        for key, value in kwargs.items():
            # Check this option already exists.
            section = lookup.get(key, None)
            if section is None:
                raise KeyError("Unknown configuration option {}.".format(key))

            # Save it.
            d[section][key] = value

        # And then read the dictionary in.
        return self.read_dict(d)


    def parsedimension(self, dim):
        """Convert a dimension to inches.

        The dimension should be in the format '<value><unit>', where the unit
        can be 'mm', 'cm', 'in', or 'pt'. If no unit is specified, it is
        assumed to be in inches. Note that points refer to TeX points (72.27
        per inch) rather than Postscript points (72 per inch).

        Parameters
        ----------
        dim: string
            The dimension to parse.

        Returns
        -------
        float: The dimension in inches.

        Raises
        ------
        DimensionError:
            The dimension is empty or not recognised.

        """
        # Need a string.
        if dim is None:
            raise DimensionError("Cannot be set to an empty value.")

        # Check for an empty string.
        dim = dim.strip().lower()
        if not dim:
            raise DimensionError("Cannot be set to an empty value.")

        # Try to parse it.
        m = self._dimre.match(dim)
        if not m:
            raise DimensionError("Could not parse {} as a dimension.".format(dim))

        # Pull out the pieces.
        groups = m.groupdict()
        size = float(groups['size'])
        unit = groups.get('unit', '') or ''
        unit = unit.lower()

        # No unit: already in inches.
        if not unit:
            return size

        # Pick out the divisor to convert into inches.
        factor = self._dimconv.get(unit, None)

        # Unknown unit.
        if factor is None:
            raise DimensionError("Unknown unit {}.".format(unit))

        # Do the conversion.
        return size / factor


    def getdimension(self, section, option, **kwargs):
        """Return a configuration entry as a dimension in inches.

        The dimension should be in the format '<value><unit>', where the unit
        can be 'mm', 'cm', 'in', or 'pt'. If no unit is specified, it is
        assumed to be in inches. Note that points refer to TeX points (72.27
        per inch) rather than Postscript points (72 per inch).

        Parameters
        ----------
        section, option: string
            The section and option keys to retrieve.

        Returns
        -------
        float: The dimension in inches.

        Raises
        ------
        DimensionError:
            The dimension is empty or not recognised.

        """
        # Get the string version of the dimension.
        dim = self.get(section, option, **kwargs)

        # And parse it; modify any parsing exception to include
        # the section and option we were parsing.
        try:
            return self.parsedimension(dim)
        except DimensionError as e:
            msg = "{}.{}: {}".format(section, option, str(e))
            raise DimensionError(msg) from None


    def getcolor(self, section, option, **kwargs):
        """Return a configuration entry as a Matplotlib color.

        Recognised color formats are:
            * Named colors (red, yellow, etc.)
            * Cycle colors (C1, C2 etc.)
            * Tuples (r, g, b) or (r, g, b, a) with floating-point entries in
              [0, 1]
            * A floating-point value in [0, 1] for grayscale
            * 'none', 'transparent', or an empty value for transparent.

        Parameters
        ----------
        section, option: string
            The section and option keys to retrieve.

        Returns
        -------
        matplotlib-compatible colour.

        Raises
        ------
        ColorError
            The value could not be interpreted as a color.

        """
        import matplotlib

        # Retrieve the string value. Empty values are interpreted as none.
        value = self.get(section, option, **kwargs).strip() or 'none'

        # Transparent.
        if value in {'none', 'transparent'}:
            return 'none'

        # Single floating point number: grayscale.
        try:
            gray = float(value)
        except ValueError:
            pass
        else:
            # For historical reasons Matlotlib requires this to be a string.
            if not (0 <= gray <= 1):
                raise ColorError("{}.{}: greyscale floats must be in [0, 1].".format(section, option))
            return value

        # Nth color in the cycle (i.e., C1, C2 etc), or a named color.
        # Unfortunately, this returns True for grayscale values outside [0, 1]
        # so we have to do our own check above.
        if matplotlib.colors.is_color_like(value):
            return value

        # Tuple or list.
        if (value[0] == '(' and value[-1] == ')') or (value[0] == '[' and value[-1] == ']'):
            entries = value[1:-1].split(',')

            # Can be RGB or RGBA.
            if not (2 < len(entries) < 5):
                raise ColorError("{}.{}: RGBA colors must have 3 or 4 entries.".format(section, option))

            # Attempt to convert to floats.
            try:
                float_entries = tuple(map(float, entries))
            except ValueError:
                raise ColorError("{}.{}: RGBA colors must be floating point.".format(section, option)) from None

            # And get Matplotlib to convert to a color.
            try:
                rgba = matplotlib.colors.to_rgba(float_entries)
            except ValueError as e:
                raise ColorError("{}.{}: {}.".format(section, option, e)) from None

            # Done.
            return rgba

        # Not a format we know.
        raise ColorError("{}.{}: could not interpret '{}' as a color.".format(section, option, value))


    def in_tracking_dir(self, type, fn):
        """Check if a file is in a tracking directory.

        Parameters
        ----------
        type : {"data", "import"}
            The type of file to check for.
        fn : path-like
            The filename to check.

        Returns
        -------
        Boolean
            True if the file is in one of the corresponding tracking
            directories specified in the configuration.

        """
        if type == "data":
            paths = self.get("paths", "data").strip().splitlines()
        elif type == "import":
            paths = self.get("paths", "pythonpath").strip().splitlines()
            paths.extend(self.get("paths", "extra_imports").strip().splitlines())
        else:
            raise ValueError("Unknown tracking type {0:s}.".format(type))

        # If the filename relative to one of these paths does not have to leave
        # the directory (i.e., doesn't start with ..) then it must be within
        # the directory.
        fn = os.path.abspath(fn)
        for path in paths:
            path = os.path.abspath(path)
            if not os.path.relpath(fn, path).startswith(".."):
                return True

        # Not in any of the directories.
        return False


# The current configuration.
_config = PgfutilsParser()

def _config_reset():
    """Internal: reset the configuration to the default state.

    """
    global _config
    _config.clear()
    _config.read_dict({
        'tex': {
            'engine': 'xelatex',
            'text_width': '345 points',
            'text_height': '550 points',
            'marginpar_width': '65 points',
            'marginpar_sep': '11 points',
            'num_columns': '1',
            'columnsep': '10 points',
        },

        'pgfutils': {
            'preamble': '',
            'preamble_substitute': 'false',
            'font_family': 'serif',
            'font_name': '',
            'font_size': '10',
            'legend_font_size': '10',
            'line_width': '1',
            'axes_line_width': '0.6',
            'legend_border_width': '0.6',
            'legend_border_color': '(0.8, 0.8, 0.8)',
            'legend_background': '(1, 1, 1)',
            'legend_opacity': 0.8,
            'figure_background': '',
            'axes_background': 'white',
            'extra_tracking': '',
            'environment': '',
        },

        'paths': {
            'data': '.',
            'pythonpath': '',
            'extra_imports': '',
        },

        'rcParams': {
        },

        'postprocessing': {
            'fix_raster_paths': 'true',
            'tikzpicture': 'false',
        }
    })


def _relative_if_subdir(fn):
    """Internal: get a relative or absolute path as appropriate.

    Parameters
    ----------
    fn : path-like
        A path to convert.

    Returns
    -------
    fn : str
        A relative path if the file is underneath the top-level project
        directory, or an absolute path otherwise.

    """
    rel = os.path.relpath(fn)
    if rel.startswith(".."):
        return os.path.abspath(fn)
    return rel


def _file_tracker(to_wrap):
    """Internal: install an opened file tracker.

    To be trackable, the given callable should return an instance of a subclass
    of `io.IOBase`. If its `writable` method returns True, it is assumed to be
    an output file, otherwise if its `readable` method returns True it is
    assumed to be an input.

    The docstring, name etc. of the given callable are copied to the wrapper
    function that performs the tracking.

    The set of files that have been opened so far are stored in the `filenames`
    attribute of this function. In general, use the _list_opened_files()
    method.

    Parameters
    ----------
    to_wrap: callable
        The callable to install the tracker around.

    Returns
    -------
    Wrapper function.

    """
    global _config

    import functools
    @functools.wraps(to_wrap)
    def wrapper(*args, **kwargs):
        # Defer opening to the real function.
        file = to_wrap(*args, **kwargs)

        # Only attempt to track files implemented as standard IO objects.
        if not isinstance(file, io.IOBase):
            return file

        # Integers indicate file objects that were created from descriptors
        # (e.g., opened with the low-level os.open() and then wrapped with
        # os.fdopen()). There is no reliable way to retrieve the filename; on
        # Linux, the command 'readlink /proc/self/fd/N' can be used provided it
        # hasn't been renamed/deleted since. I'm leaving this as unimplemented
        # until I find an actual usecase for doing it...
        if isinstance(file.name, int):
            return file

        # If a file is writeable; this includes files opened in r+ or append
        # modes. We assume these can't be dependencies.
        if file.writable():
            # Does it match the filename pattern used by the PGF backend for
            # rasterised parts of the image being saved as PNGs?
            if re.match(r"^.+-img\d+.png$", file.name):
                _file_tracker.filenames.add(("w", _relative_if_subdir(file.name)))

        # Should always be readable in this case, but check anyway.
        elif file.readable() and _config.in_tracking_dir("data", file.name):
            _file_tracker.filenames.add(("r", _relative_if_subdir(file.name)))

        # Done.
        return file

    # Return the wrapper function.
    return wrapper

# Initialise the set of opened files.
_file_tracker.filenames = set()


class ImportTracker(importlib.abc.MetaPathFinder):
    """Import finder which tracks imported files in configured paths.

    """
    def __init__(self):
        super().__init__()
        self._avoid_recursion = set()
        self.imported = set()

    def find_spec(self, fullname, path, target=None):
        # According to PEP451, this is mostly intended for a reload. I can't
        # see a way (without calling importlib._bootstrap._find_spec, which
        # should not be imported according to the note at the top of the
        # module) to pass this information on. Hence, lets skip tracking in
        # this case.
        if target is not None:  # pragma: no cover
            return None

        # We use importlib to find the actual spec, so we need to avoid
        # recursing when this finder is called again.
        if fullname in self._avoid_recursion:
            return None

        # Find the spec.
        self._avoid_recursion.add(fullname)
        spec = importlib.util._find_spec_from_path(fullname, path)
        self._avoid_recursion.remove(fullname)

        # If it has an origin in one of our tracked dirs, log it.
        if spec is not None and spec.origin is not None:
            global _config
            if _config.in_tracking_dir("import", spec.origin):
                _file_tracker.filenames.add(("r", _relative_if_subdir(spec.origin)))

        # And return the result.
        return spec


def _install_standard_file_trackers():
    """Internal: install standard file trackers in likely locations.

    This wraps the standard open() function as well as the io.open() function.
    This seems to catch all uses of the standard NumPy `load` (for both .npy
    and .npz files) and `loadtxt`, and should also work for most libraries
    which use Python functions to open files. It won't work for anything
    which uses low-level methods, either through the `os` module or at C level
    in compiled modules.

    Note: this needs to be run prior to importing NumPy (and therefore prior to
    importing Matplotlib) as NumPy's data loader module stores a reference to
    io.open which wouldn't get wrapped.

    """
    import builtins
    import io
    builtins.open = _file_tracker(builtins.open)
    io.open = _file_tracker(io.open)
    if hasattr(pathlib, "_normal_accessor"):
        pathlib._normal_accessor.open = _file_tracker(pathlib._normal_accessor.open)
    sys.meta_path.insert(0, ImportTracker())


def _install_extra_file_trackers(trackers):
    """Internal: install requested extra file trackers.

    Parameters
    ----------
    trackers : list
        List of strings containing the names of the extra trackers to install.
        Names are not case-sensitive. Currently only "netCDF4" is supported.

    """
    for tracker in trackers:
        tracker = tracker.strip().lower()

        # netCDF4 data storage.
        if tracker == "netcdf4":
            import netCDF4

            # Wrap the Dataset class to modify its initialiser to track read
            # files. The class is part of the compiled extension so we can't
            # just override the initialiser.
            class PgfutilsTrackedDataset(netCDF4.Dataset):
                def __init__(self, filename, mode="r", **kwargs):
                    super().__init__(filename, mode=mode, **kwargs)
                    if mode == "r":
                        _file_tracker.filenames.add(("r", filename))
            netCDF4.Dataset = PgfutilsTrackedDataset

            # Same deal for the MFDataset (multiple files read as one dataset).
            class PgfutilsTrackedMFDataset(netCDF4.MFDataset):
                def __init__(self, files, *args, **kwargs):
                    super().__init__(files, *args, **kwargs)

                    # Single string: glob pattern to expand.
                    if isinstance(files, str):
                        import glob
                        files = glob.glob(files)

                    # And track them all.
                    for fn in files:
                        _file_tracker.filenames.add(("r", fn))
            netCDF4.MFDataset = PgfutilsTrackedMFDataset

        else:
            raise ValueError("Unknown extra tracker {}".format(tracker))


def add_dependencies(*args):
    """Add a file dependency for the current figure.

    In most situations, the in-built file tracking should suffice. However,
    some files can be missed (for example, if a library you are using has its
    file opening routines in a compiled extension rather than using Python
    functions). This function can be used to manually add these files to the
    dependencies of the current figure.

    Parameters
    ----------
    fn : string
        The filename of the dependency, relative to the top-level directory of
        the project.

    """
    for fn in args:
        _file_tracker.filenames.add(("r", fn))


def _list_opened_files():
    """Internal: get project files which were opened by the script.

    Returns
    -------
    list
        A list of tuples (mode, filename) of files in or under the current
        directory. Entries with mode 'r' were opened for reading and are
        assumed to be dependencies of the generated figure. Entries with mode
        'w' were opened for writing and are rasterised graphics included in the
        final figure. The list is sorted by mode and then filename.

    """
    return sorted(_file_tracker.filenames)


# If the script has been run in an interactive mode (currently, if it is
# running under IPython in a mode with an event loop) then we will display the
# figure in the save() call rather than saving it.
# Interactivity is tested each time setup_figure() is called. This global
# stores the latest result to avoid running the test twice (we need it in
# setup_figure() to avoid setting the backend if interactive, and then in
# save()).
_interactive = False


def setup_figure(width=1.0, height=1.0, columns=None, margin=False,
                 full_width=False, **kwargs):
    """Set up matplotlib figures for PGF output.

    This function should be imported and run before you import any matplotlib
    code. Figure properties can be passed in as keyword arguments to override
    the project configuration.

    Parameters
    ----------
    width, height : float or string
        If a float, the fraction of the corresponding text width or height that
        the figure should take up. If a string, a dimension in centimetres
        (cm), millimetres (mm), inches (in) or points (pt). For example, '3in'
        or '2.5 cm'.
    columns : integer, optional
        The number of columns the figure should span. This should be between 1
        and the total number of columns in the document (as specified in the
        configuration). A value of None corresponds to spanning all columns.
        Any other value results in a ValueError being raised.
    margin : Boolean, default False
        If True, a margin figure (i.e., one to fit within the margin notes in
        the document) is generated. If the width is a fraction, it is treated
        as a fraction of the marginpar_width configuration setting. The height
        is still treated as a fraction of the text height. The columns setting
        is ignored if this is True.
    full_width : Boolean, default False
        If True, a full-width figure, i.e., one spanning the main text, the
        margin notes, and the separator between them, is generated. A
        fractional width is treated relative to the full width. The height is
        still treated as a fraction of the text height. The columns and margin
        parameters are ignored if this is True.

    """
    global _config, _interactive

    # Reset the configuration.
    _config_reset()

    # Load configuration from a local file if one exists.
    if os.path.exists('pgfutils.cfg'):
        _config.read('pgfutils.cfg')
        _file_tracker.filenames.add(("r", "pgfutils.cfg"))

    # And anything given in the function call.
    if kwargs:
        _config.read_kwargs(**kwargs)

    # Set environment variables specified in the configuration.
    for line in _config['pgfutils']['environment'].splitlines():
        line = line.strip()
        if not line:
            continue

        # Check the variables are formatted correctly.
        if '=' not in line:
            raise ValueError(
                "Environment variables should be in the form NAME=VALUE. "
                "The line '{}' does not match this.".format(line)
            )

        # And set them.
        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip()

    # Install file trackers if desired. This must be done before anything which
    # imports Matplotlib.
    if 'PGFUTILS_TRACK_FILES' in os.environ:
        _install_standard_file_trackers()
        extra = _config['pgfutils']['extra_tracking'].strip()
        if extra:
            _install_extra_file_trackers(extra.split(","))

    # Reset our interactive flag on each call.
    _interactive = False

    # If we're running under IPython, see if there is an event loop in use.
    # Unfortunately, the matplotlib.rcParams['interactive'] (or equivalently,
    # matplotlib.is_interactive()) don't appear to propagate when IPython runs
    # a script so we can't test those.
    try:
        ipython = get_ipython()
    except NameError:
        pass
    else:
        if ipython.active_eventloop is not None:            # pragma: no cover
            _interactive = True

    # Add any desired entries to sys.path.
    for newpath in _config['paths']['pythonpath'].splitlines():
        newpath = newpath.strip()
        if newpath:
            sys.path.insert(0, newpath)

    # We're now ready to start configuring Matplotlib.
    import matplotlib

    # Set the backend. We don't want to overwrite the current backend if this
    # is an interactive run as the PGF backend does not implement a GUI.
    if not _interactive:                              # pragma: no cover
        matplotlib.use('pgf')

    # Specify which TeX engine we are using.
    matplotlib.rcParams['pgf.texsystem'] = _config['tex']['engine']

    # Custom TeX preamble.
    preamble = _config['pgfutils']['preamble']
    if _config['pgfutils'].getboolean('preamble_substitute'):
        preamble = string.Template(preamble).substitute(basedir=os.path.abspath('.'))
    matplotlib.rcParams['pgf.preamble'] = preamble

    # Clear the existing lists of specific font names.
    matplotlib.rcParams['font.sans-serif'] = []
    matplotlib.rcParams['font.serif'] = []
    matplotlib.rcParams['font.cursive'] = []
    matplotlib.rcParams['font.monospace'] = []
    matplotlib.rcParams['font.fantasy'] = []

    # Don't let the backend try to load fonts.
    matplotlib.rcParams['pgf.rcfonts'] = False

    # Set the font family in use.
    matplotlib.rcParams['font.family'] = _config['pgfutils']['font_family']

    # If a specific font was given, add it to the list of fonts for
    # the chosen font family.
    if _config['pgfutils']['font_name']:
        k = 'font.{}'.format(_config['pgfutils']['font_family'])
        matplotlib.rcParams[k].append(_config['pgfutils']['font_name'])

    # Set the font sizes.
    matplotlib.rcParams['font.size'] = _config['pgfutils'].getfloat('font_size')
    matplotlib.rcParams['legend.fontsize'] = _config['pgfutils'].getfloat('legend_font_size')

    # Don't use Unicode in the figures. If this is not disabled, the PGF
    # backend can replace some characters with unicode variants, and these
    # don't always play nicely with some TeX engines and/or fonts.
    matplotlib.rcParams['axes.unicode_minus'] = False

    # Line widths.
    matplotlib.rcParams['axes.linewidth'] = _config['pgfutils'].getfloat('axes_line_width')
    matplotlib.rcParams['lines.linewidth'] = _config['pgfutils'].getfloat('line_width')

    # Colours.
    matplotlib.rcParams['figure.facecolor'] = _config['pgfutils'].getcolor('figure_background')
    matplotlib.rcParams['savefig.facecolor'] = _config['pgfutils'].getcolor('figure_background')
    matplotlib.rcParams['axes.facecolor'] = _config['pgfutils'].getcolor('axes_background')

    # Now we need to figure out the total width available for the figure, i.e.,
    # the width corresponding to the figure parameter being 1.
    # First, look up some document properties.
    text_width = _config['tex'].getdimension('text_width')
    margin_width = _config['tex'].getdimension('marginpar_width')
    margin_sep = _config['tex'].getdimension('marginpar_sep')
    num_columns = _config['tex'].getint('num_columns')

    # Full-width figure.
    if full_width:
        available_width = text_width + margin_sep + margin_width

    # Making a margin figure.
    elif margin:
        available_width = margin_width

    # Columns not specified, or spanning all available.
    elif columns is None or columns == num_columns:
        available_width = text_width

    # More columns than present in the document.
    elif columns > num_columns:
        msg = "Document has {} columns, but you asked for a figure spanning {} columns."
        raise ValueError(msg.format(num_columns, columns))

    # Not sure what this would mean.
    elif columns < 1:
        raise ValueError("Number of columns must be at least one.")

    # A number of columns less than the total.
    else:
        # Figure out the width of each column. N columns have
        # N - 1 separators between them.
        columnsep = _config['tex'].getdimension('columnsep')
        total_columnsep = columnsep * (num_columns - 1)
        total_columnw = text_width - total_columnsep
        column_width = total_columnw / num_columns

        # And the width (including the separators between them)
        # of the requested number of columns.
        available_width = (column_width * columns) + (columnsep * (columns - 1))

    # And now we can calculate the actual figure width. If it is a float, it is
    # a fraction of the total available width.  Otherwise, assume it's an
    # explicit dimension.
    try:
        w = float(width)
    except ValueError:
        w = _config.parsedimension(width)
    else:
        w *= available_width

    # And the figure height.
    try:
        h = float(height)
    except ValueError:
        h = _config.parsedimension(height)
    else:
        h *= _config['tex'].getdimension('text_height')

    # Set the figure size.
    matplotlib.rcParams['figure.figsize'] = [w, h]

    # Ask for a tight layout (i.e., minimal padding).
    matplotlib.rcParams['figure.autolayout'] = True

    # Copy any specific rcParams the user set.
    matplotlib.rcParams.update(_config['rcParams'])


def save(figure=None):
    """Save the figure.

    The filename is based on the name of the script which calls this function.
    For example, if you call save() from a script named sine.py, then the saved
    figure will be sine.pgf.

    Parameters
    ----------
    figure: matplotlib Figure object, optional
        If not given, then the current figure -- as returned by
        matplotlib.pyplot.gcf() -- will be saved.

    """
    global _config, _interactive

    from matplotlib import pyplot as plt, __version__ as mpl_version

    # Get the current figure if needed.
    if figure is None:
        figure = plt.gcf()

    # Go through and fix up a few little quirks on the axes within this figure.
    for axes in figure.get_axes():
        # There are no rcParams for the legend properties. Go through and set
        # these directly before we save.
        legend = axes.get_legend()
        if legend:
            frame = legend.get_frame()
            frame.set_linewidth(_config['pgfutils'].getfloat('legend_border_width'))
            frame.set_alpha(_config['pgfutils'].getfloat('legend_opacity'))
            frame.set_ec(_config['pgfutils'].getcolor('legend_border_color'))
            frame.set_fc(_config['pgfutils'].getcolor('legend_background'))

        # Some PDF viewers show white lines through vector colorbars. This is a
        # bug in the viewers, but can be worked around by forcing the edge of
        # the patches in the colorbar to have the same colour as their faces.
        # This doesn't work with partially transparent (alpha < 1) images. As
        # of matplotlib v1.5.0, colorbars with many patches (> 50 by default)
        # are rasterized and included as PNGs so this workaround is not needed
        # in most cases.
        #
        # http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.colorbar
        # https://github.com/matplotlib/matplotlib/issues/1188
        # https://github.com/matplotlib/matplotlib/pull/4481
        # https://github.com/matplotlib/matplotlib/commit/854f74a

        # Gather a set of colorbars.  This includes colorbars from images
        # (imshow etc), collections (e.g., scatter plots), and contour plot
        # lines (the roundabout _current_image way -- there doesn't appear to
        # be any other reference from the axes to the QuadContourSet object).
        colorbars = set()
        colorbars.update(im.colorbar for im in axes.images if im.colorbar)
        colorbars.update(coll.colorbar for coll in axes.collections if coll.colorbar)
        if axes._current_image and axes._current_image.colorbar:
            colorbars.add(axes._current_image.colorbar)

        # And process them.
        for cb in colorbars:
            if not cb.solids:
                continue
            # Ignore rasterized or transparent colorbars.
            # Note that alpha=None is the same as alpha=1.
            if cb.solids.get_rasterized():
                continue
            if (cb.alpha or 1.0) < 1.0:
                continue
            cb.solids.set_edgecolor('face')

    # Interactive mode: show the figure rather than saving.
    if _interactive:                     # pragma: no cover
        plt.show()
        return

    # Look at the next frame up for the name of the calling script.
    script = inspect.getfile(sys._getframe(1))
    name, ext = os.path.splitext(script)

    # The initial Matplotlib output file, and the final figure file.
    mpname = name + ".pgf"
    figname = name + ".pypgf"

    # Get Matplotlib to save it.
    figure.savefig(mpname)

    # We have been tracking opened files and need to
    # output our results.
    if 'PGFUTILS_TRACK_FILES' in os.environ:
        # The files.
        files = '\n'.join([':'.join(f) for f in _list_opened_files()])

        # Figure out where to print it.
        dest = os.environ.get('PGFUTILS_TRACK_FILES') or '1'

        # stdout.
        if dest == '1':
            sys.stdout.write(files)

        # stderr.
        elif dest == '2':
            sys.stderr.write(files)

        # A named file.
        else:
            with open(dest, 'w') as f:
                f.write(files)

    # List of all postprocessing functions we are running on this figure.
    # Each should take in a single line as a string, and return the line with
    # any required modifications.
    pp_funcs = []

    # Local cache of postprocessing options.
    fix_raster_paths = _config['postprocessing'].getboolean('fix_raster_paths')
    tikzpicture = _config['postprocessing'].getboolean('tikzpicture')

    # Add the appropriate directory prefix to all raster images
    # included via \pgfimage.
    if fix_raster_paths:
        figdir = os.path.dirname(figname) or '.'

        # Only apply this if the figure is not in the top-level directory.
        if not os.path.samefile(figdir, os.curdir):
            prefix = os.path.relpath(figdir)
            expr = re.compile(r"(\\(?:pgfimage|includegraphics)(?:\[.+?\])?{)(.+?)}")
            repl = r"\1{0:s}/\2}}".format(prefix)
            pp_funcs.append(lambda s: re.sub(expr, repl, s))

    # Use the tikzpicture environment rather than pgfpicture.
    if tikzpicture:
        expr = re.compile(r"\\(begin|end){pgfpicture}")
        repl = r"\\\1{tikzpicture}"
        pp_funcs.append(lambda s: re.sub(expr, repl, s))

    # Postprocess the figure, moving it into the final destination.
    with open(mpname, 'r') as infile, open(figname, 'w') as outfile:

        # Make some modifications to the header.
        line = infile.readline()
        while line[0] == '%':
            # Update the creator line to include pgfutils version, and add a
            # line with the path of the script that created the figure.
            if "Creator:" in line:
                outfile.write(line[:-1])
                outfile.write(" v")
                outfile.write(mpl_version)
                outfile.write(", matplotlib-pgfutils v")
                outfile.write(__version__)
                outfile.write('\n%%  Script: ')
                outfile.write(os.path.abspath(script))
                outfile.write('\n')

            # Update the \input instructions.
            elif r"\input{<filename>.pgf}" in line:
                outfile.write("%%   \\input{")
                outfile.write(figname)
                outfile.write("}\n")

            # If we're changing the figure to use the tikzpicture environment, we also
            # need to update the required package.
            elif tikzpicture and r"\usepackage{pgf}" in line:
                outfile.write("%%    \\usepackage{tikz}\n")

            # If we're fixing the paths to rasterised images, we can remove the
            # instructions about using the import package.
            elif fix_raster_paths and line.startswith("%% Figures using additional raster"):
                while r"\import{<path to file>}" not in line:
                    line = infile.readline()

                # Discard blank line after the statement too.
                infile.readline()

            # Copy the original line.
            else:
                outfile.write(line)

            # Next line of header.
            line = infile.readline()

        # Post-process and write the first line after the header.
        for func in pp_funcs:
            line = func(line)
        outfile.write(line)

        # Apply the postprocessing to the remainder of the file.
        for line in infile:
            for func in pp_funcs:
                line = func(line)
            outfile.write(line)

    # Delete the original file.
    os.remove(mpname)
