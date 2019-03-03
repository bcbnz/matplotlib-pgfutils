# Copyright 2018, 2019 Blair Bonnett
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

# We don't import Matplotlib here as this brings in NumPy. In turn, NumPy
# caches a reference to the io.open() method as part of its data loading
# functions. This means we can't (reliably) wrap all loading functions if we're
# asked to track opened files. Instead, the tracking is installed in
# setup_figure() before the first import of Matplotlib (assuming the user
# doesn't use our internal functions). Python's caching of imported modules
# means there should be minimal impact from importing Matplotlib separately in
# different functions.

import configparser
import inspect
import os
import os.path
import re
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
        # Check for an empty string.
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
        dim = self.get(section, option, **kwargs).strip().lower()

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
           'num_columns': '1',
           'columnsep': '10 points',
        },

        'pgfutils': {
           'preamble': '',
           'font_family': 'serif',
           'font_name': '',
           'font_size': '10',
           'legend_font_size': '10',
           'line_width': '1',
           'axes_line_width': '0.6',
           'figure_background': '',
           'axes_background': 'white',
       },

       'rcParams': {
       },

       'postprocessing': {
           'fix_raster_paths': 'true',
           'tikzpicture': 'false',
       }
    })


def _file_tracker(to_wrap):
    """Internal: install an opened file tracker.

    To be trackable, the given callable should return some object with `name`
    and `mode` attributes representing the filename and mode of the opened
    file.

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
    import functools
    @functools.wraps(to_wrap)
    def wrapper(*args, **kwargs):
        # Defer opening to the real function.
        file = to_wrap(*args, **kwargs)

        # Standard IO readers store what we need in name and mode attributes.
        if not hasattr(file, 'name') or not hasattr(file, 'mode'):
            return file

        # Integers indicate file objects that were created from descriptors
        # (e.g., opened with the low-level os.open() and then wrapped with
        # os.fdopen()). There is no reliable way to retrieve the filename; on
        # Linux, the command 'readlink /proc/self/fd/N' can be used provided it
        # hasn't been renamed/deleted since. I'm leaving this as unimplemented
        # until I find an actual usecase for doing it...
        if isinstance(file.name, int):
            return file

        # Everything we are interested in is within the project tree.
        if os.path.relpath(file.name).startswith('.'):
            return file

        # Assume files that are read are dependencies.
        if 'r' in file.mode:
            _file_tracker.filenames.add(("r", file.name))

        # Binary files being written could be rasterised parts of the image
        # being saved as PNGs. Confirm this by checking the filename against
        # the pattern that the PGF backend uses.
        elif file.mode == 'wb':
            if re.match(r"^.+-img\d+.png$", file.name):
                _file_tracker.filenames.add(("w", file.name))

        # Done.
        return file

    # Return the wrapper function.
    return wrapper

# Initialise the set of opened files.
_file_tracker.filenames = set()


def _install_file_trackers():
    """Internal: install file trackers in likely locations.

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


def setup_figure(width=1.0, height=1.0, **kwargs):
    """Set up matplotlib figures for PGF output.

    This function should be imported and run before you import any matplotlib
    code. Figure properties can be passed in as keyword arguments to override
    the project configuration.

    Parameters
    ----------
    width, height: float or string
        If a float, the fraction of the corresponding text width or height that
        the figure should take up. If a string, a dimension in centimetres
        (cm), millimetres (mm), inches (in) or points (pt). For example, '3in'
        or '2.5 cm'.

    """
    global _config, _interactive

    # Need to install our file trackers (if desired)
    # before we import Matplotlib.
    if 'PGFUTILS_TRACK_FILES' in os.environ:
        _install_file_trackers()

    # Reset the configuration.
    _config_reset()

    # Load configuration from a local file if one exists.
    if os.path.exists('pgfutils.cfg'):
        _config.read('pgfutils.cfg')

    # And anything given in the function call.
    if kwargs:
        _config.read_kwargs(**kwargs)

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
        if ipython.active_eventloop is not None:
            _interactive = True

    # We're now ready to start configuring Matplotlib.
    import matplotlib

    # Set the backend. We don't want to overwrite the current backend if this
    # is an interactive run as the PGF backend does not implement a GUI.
    if not _interactive:
        matplotlib.use('pgf')

    # Specify which TeX engine we are using.
    matplotlib.rcParams['pgf.texsystem'] = _config['tex']['engine']

    # Custom TeX preamble.
    matplotlib.rcParams['pgf.preamble'] = _config['pgfutils']['preamble']

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

    # Figure out the figure width. If it is a float, it is a fraction of
    # textwidth.  Otherwise, assume it's an explicit dimension.
    try:
        w = float(width)
    except ValueError:
        w = _config.parsedimension(width)
    else:
        w *= _config['tex'].getdimension('text_width')

    # And repeat for the figure height.
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

    import matplotlib
    from matplotlib import pyplot as plt

    # Get the current figure if needed.
    if figure is None:
        figure = plt.gcf()

    # Go through and fix up a few little quirks on the axes within this figure.
    for axes in figure.get_axes():
        # There is no rcParam setting for the line width of a border around a
        # legend. Manually set this to the axes line width.
        legend = axes.get_legend()
        if legend:
            legend.get_frame().set_linewidth(matplotlib.rcParams['axes.linewidth'])

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
    if _interactive:
        plt.show()
        return

    # Look at the next frame up for the name of the calling script.
    name, ext = os.path.splitext(inspect.getfile(sys._getframe(1)))

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

    # Add the appropriate directory prefix to all raster images
    # included via \pgfimage.
    if _config['postprocessing'].getboolean('fix_raster_paths'):
        figdir = os.path.dirname(figname) or '.'

        # Only apply this if the figure is not in the top-level directory.
        if not os.path.samefile(figdir, os.curdir):
            prefix = os.path.relpath(figdir)
            expr = re.compile(r"(\\pgfimage(?:\[.+?\])?{)(.+?)}")
            repl = r"\1{0:s}/\2".format(prefix)
            pp_funcs.append(lambda s: re.sub(expr, repl, s))

    # Use the tikzpicture environment rather than pgfpicture.
    if _config['postprocessing'].getboolean('tikzpicture'):
        expr = re.compile(r"\\(begin|end){pgfpicture}")
        repl = r"\\\1{tikzpicture}"
        pp_funcs.append(lambda s: re.sub(expr, repl, s))

    # Postprocess the figure, moving it into the final destination.
    with open(mpname, 'r') as infile, open(figname, 'w') as outfile:
        # Update the creator line at the start of the header.
        line = infile.readline()[:-1]
        outfile.write(line)
        outfile.write(", matplotlib-pgfutils\n")

        # Update the \input instructions.
        outfile.write(infile.readline())
        outfile.write(infile.readline())
        _ = infile.readline()
        outfile.write("%%   \\input{")
        outfile.write(figname)
        outfile.write("}\n")

        # Copy the preamble instructions.
        outfile.write(infile.readline())
        outfile.write(infile.readline())
        line = infile.readline()
        if _config['postprocessing'].getboolean('tikzpicture'):
            outfile.write("%%   \\usepackage{tikz}\n")
        else:
            outfile.write(line)
        outfile.write(infile.readline())

        # If we've updated the raster image directory, we can delete the
        # instructions about getting them to appear.
        if _config['postprocessing'].getboolean('fix_raster_paths'):
            for n in range(7):
                _ = infile.readline()

        # Otherwise we need to copy them over.
        else:
            for n in range(7):
                outfile.write(infile.readline())

        # Ignore the rest of the header (which includes the preamble which was
        # used). The first non-header line is \begingroup which we don't want
        # to change anyway.
        line = infile.readline()
        while line[0] == '%':
            outfile.write(line)
            line = infile.readline()
        outfile.write(line)

        # Apply the postprocessing to the remainder of the file.
        for line in infile:
            for func in pp_funcs:
                line = func(line)
            outfile.write(line)

    # Delete the original file.
    os.remove(mpname)
