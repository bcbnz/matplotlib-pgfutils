# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

"""Utilities for generating PGF plots from matplotlib.

From version 1.2, matplotlib has included a PGF backend. This exports figures as drawing
commands for the PGF drawing package for LaTeX, allowing LaTeX to typeset the image.
This module provides some utilities to simplify creating PGF figures from scripts (so
they can be processed via Makefiles) in order to get consistent-looking plots.

"""

__version__ = "2.0.0.dev0"

import ast
import builtins
from collections.abc import Mapping
import functools
import inspect
import io
import os
from pathlib import Path
import re
import string
import sys
import tomllib
from typing import Any, Callable, Literal, TypedDict, get_args, get_origin
import warnings


class Tracker:
    """Track files that are read, written or imported.

    This can then be used for generating dependency lists. Note that the tracker does
    not filter the files; that is up to the user. Functions must be wrapped before use.

    """

    @property
    def imported(self) -> set[Path]:
        """Absolute paths to modules that were imported.

        This iterates over all modules cached in `sys.modules` and finds the paths to
        each module. Any modules which don't have a filesystem path specified will be
        ignored.

        """
        paths = set()

        for mod in sys.modules.values():
            if mod.__spec__ is None or mod.__spec__.origin is None:
                continue

            path = Path(mod.__spec__.origin)
            if path.exists() and path.is_file():
                paths.add(path.resolve())

        return paths

    # Files that were opened in a read mode.
    read: set[Path]

    # Files that were explicitly added as dependencies.
    explicit_dependencies: set[Path]

    # Files that were opened in a write mode.
    written: set[Path]

    # For avoid recursion when tracking imports.
    _avoid_recursion: set[str]

    def __init__(self):
        super().__init__()
        self.read = set()
        self.explicit_dependencies = set()
        self.written = set()

    def add_dependencies(self, *args: os.PathLike[str] | str):
        """Add a file dependency for the current figure.

        In most situations, the in-built file tracking should suffice. However, some
        files can be missed (for example, if a library you are using has its file
        opening routines in a compiled extension rather than using Python functions).
        This function can be used to manually add these files to the dependencies of the
        current figure.

        Parameters
        ----------
        *args
            Filenames to add as dependencies. Relative filenames will be expanded from
            the current working directory.

        """
        for fn in args:
            self.explicit_dependencies.add(Path(fn).resolve())

    def wrap_file_opener[**P, R](self, opener: Callable[P, R]) -> Callable[P, R]:
        """Wrap a function which opens files for tracking.

        To be trackable, the objects returned by `opener` should be instances of
        `io.IOBase` which provide a `name` property giving the filename. If the objects
        `writable` method returns True, the filename is added to the `written` set, and
        otherwise if the `readable` method returns True the filename is added to the
        `read` set. Note that this means files opened in `r+` or append modes are only
        added to `written`.

        Parameters
        ----------
        opener
            A function which opens files.

        Returns
        -------
        wrapped_opener
            A wrapper around the opener which takes the same inputs and returns the same
            output, but tracks the filenames it is used for.

        """

        @functools.wraps(opener)
        def wrapper(*args, **kwargs):
            # Defer opening to the wrapped function.
            file = opener(*args, **kwargs)

            # Only deal with IO objects that give us the filename.
            if not isinstance(file, io.IOBase):
                return file
            filename = getattr(file, "name")
            if filename is None:
                return file

            # Integers indicate file objects that were created from descriptors (e.g.,
            # opened with the low-level os.open() and then wrapped with os.fdopen()).
            # There is no reliable way to retrieve the filename; on Linux, the command
            # 'readlink /proc/self/fd/N' can be used provided it hasn't been
            # renamed/deleted since.  I'm leaving this as unimplemented until I find an
            # actual usecase.
            if isinstance(filename, int):
                return file

            # Writable modes include r+ or append modes; treat these solely as writes.
            if file.writable():
                self.written.add(Path(filename).resolve())
            elif file.readable():
                self.read.add(Path(filename).resolve())

            return file

        return wrapper


# Create a tracker and start tracking from common locations.
tracker = Tracker()
builtins.open = tracker.wrap_file_opener(builtins.open)
io.open = tracker.wrap_file_opener(io.open)

# Now we can import Matplotlib. We couldn't do so earlier as it brings in NumPy, which
# in turn caches references to io.open() and so would prevent us reliably tracking data
# files it opens.
import matplotlib  # noqa: E402


class DimensionError(ValueError):
    """A specification could not be converted to a dimension."""

    pass


class ColorError(ValueError):
    """A specification could not be converted to a color."""

    pass


class ConfigError(ValueError):
    """An error detected in the configuration."""

    def __init__(self, section: str, key: str, message: str):
        raise super().__init__(f"{section}.{key}: {message}")


def parse_color(spec: Literal["none", "transparent"] | str | float | tuple[float, ...]):
    """Parse a color specification to a Matplotlib color.

    Recognised color formats are:
        * Named colors (red, yellow, etc.)
        * Cycle colors (C1, C2 etc.)
        * Tuples (r, g, b) or (r, g, b, a) with floating-point entries in [0, 1]
        * A floating-point value in [0, 1] for grayscale
        * 'none', 'transparent', or an empty value for transparent

    Parameters
    ----------
    spec
        The color specification to parse.

    Returns
    -------
    matplotlib-compatible colour.

    Raises
    ------
    ColorError
        The value could not be interpreted as a color.

    """
    if isinstance(spec, list):
        spec = tuple(spec)

    # Transparent.
    if spec in {"none", "transparent", ""}:
        return "none"

    # Single floating point number: grayscale.
    try:
        gray = float(spec)
    except (TypeError, ValueError):
        pass
    else:
        if not (0 <= gray <= 1):
            raise ColorError("greyscale floats must be in [0, 1]")

        # For historical reasons Matlotlib requires this to be a string.
        return str(gray)

    # Nth color in the cycle (i.e., C1, C2 etc), or a named color. Unfortunately,
    # this returns True for grayscale values outside [0, 1] so we have to do our own
    # check above.
    if matplotlib.colors.is_color_like(spec):
        return spec

    # Any other string we accept is valid Python syntax, so parse it.
    if isinstance(spec, str):
        try:
            spec = ast.literal_eval(spec)
        except (SyntaxError, TypeError, ValueError):
            raise ColorError(f"could not interpret '{spec}' as a color.")

    # Needs to be a list or tuple of channel values.
    if not isinstance(spec, (list, tuple)):
        raise ColorError(f"could not interpret '{spec}' as a color.")

    # Filter out Booleans which Matplotlib would treat as 0 or 1.
    if any(isinstance(entry, bool) for entry in spec):
        raise ColorError(f"could not interpret '{spec}' as a color.")

    # And get Matplotlib to convert to a color.
    try:
        return matplotlib.colors.to_rgba(spec)
    except ValueError as e:
        raise ColorError(str(e))


# Recognise pieces of a dimension string.
dimension_pieces = re.compile(r"^\s*(?P<size>\d+(?:\.\d*)?)\s*(?P<unit>.+?)?\s*$")

# Divisors to convert from a unit to inches.
dimension_divisor = {
    "cm": 2.54,
    "centimetre": 2.54,
    "centimeter": 2.54,
    "centimetres": 2.54,
    "centimeters": 2.54,
    "mm": 25.4,
    "millimetre": 25.4,
    "millimeter": 25.4,
    "millimetres": 25.4,
    "millimeters": 25.4,
    "in": 1,
    "inch": 1,
    "inches": 1,
    "pt": 72.27,  # Printers points, not the 1/72 Postscript/PDF points.
    "point": 72.27,
    "points": 72.27,
}


def parse_dimension(spec: str) -> float:
    """Parse a dimension specification to TeX points.

    Matplotlib uses inches for physical sizes. This function allows other units to be
    specified and converts them to inches. Note that points are assumed to be TeX points
    (72.27 per inch) rather than Postscript points (72 per inch).

    Parameters
    ----------
    spec
        A dimension specification. This should be in the format "<value><unit>" where
        the unit can be any of the keys from the `dimension_divisor` dictionary.
        Whitespace is allowed between the value and unit. If no unit is given, it is
        assumed to be inches.

    Returns
    -------
    float
        The dimension in inches.

    """
    match = dimension_pieces.match(spec)
    if not match:
        raise DimensionError(f"could not parse {spec} as a dimension")

    # Get the components.
    groups = match.groupdict()
    size = float(groups["size"])
    unit: str = (groups.get("unit") or "").lower()

    # Assume already in inches.
    if not unit:
        return size

    # Convert with the divisor.
    factor = dimension_divisor.get(unit)
    if factor is None:
        raise DimensionError(f"unknown unit in {spec}")
    return size / factor


# Subtypes used to mark entries which should be converted when loaded.
type Dimension = float
type Color = tuple[float]


class PathConfig(TypedDict):
    """Path configuration options."""

    data: str
    pythonpath: str
    extra_imports: str


class PGFUtilsConfig(TypedDict):
    """Configuration of pgfutils behaviour."""

    preamble: str
    preamble_substitute: bool
    font_family: Literal["serif", "sans-serif", "monospace", "cursive", "fantasy"]
    font_name: str
    font_size: float
    legend_font_size: float
    line_width: float
    axes_line_width: float
    legend_border_width: float
    legend_border_color: Color
    legend_background: Color
    legend_opacity: float
    figure_background: Color
    axes_background: Color
    extra_tracking: str
    environment: str


class PostProcessingConfig(TypedDict):
    """Post-processing options."""

    fix_raster_paths: bool
    tikzpicture: bool


class TexConfig(TypedDict):
    """Configuration of the TeX system used to compile the final document."""

    engine: Literal["lualatex", "pdflatex", "xelatex"]
    text_height: Dimension
    text_width: Dimension
    marginpar_width: Dimension
    marginpar_sep: Dimension
    num_columns: int
    columnsep: Dimension


class Config:
    """Overall configuration of pgfutils."""

    paths: PathConfig
    pgfutils: PGFUtilsConfig
    post_processing: PostProcessingConfig
    tex: TexConfig
    rcparams: dict[str, dict[str, Any]]

    def __init__(self, load_file: bool = True) -> None:
        """
        Parameters
        ----------
        load_file
            If True, look for a file named `pgfutils.toml` in the current working
            directory and load it after setting the defaults.

        """
        self.paths = dict(data=".", pythonpath="", extra_imports="")
        self.pgfutils = dict(
            preamble="",
            preamble_substitute=False,
            font_family="serif",
            font_name="",
            font_size=10.0,
            legend_font_size=10.0,
            line_width=1.0,
            axes_line_width=0.6,
            legend_border_width=0.6,
            legend_border_color=parse_color("0.8"),
            legend_background=parse_color("white"),
            legend_opacity=0.8,
            figure_background=parse_color("transparent"),
            axes_background=parse_color("white"),
            extra_tracking="",
            environment="",
        )
        self.post_processing = dict(fix_raster_paths=True, tikzpicture=False)
        self.rcparams = {}
        self.tex = dict(
            engine="xelatex",
            text_height=parse_dimension("550 points"),
            text_width=parse_dimension("345 points"),
            marginpar_width=parse_dimension("65 points"),
            marginpar_sep=parse_dimension("11 points"),
            num_columns=1,
            columnsep=parse_dimension("10 points"),
        )

        if load_file:
            cfg_path = Path("pgfutils.toml")
            if cfg_path.exists():
                if not cfg_path.is_file():
                    raise RuntimeError("pgfutils.toml exists but is not a file.")
                self.load(cfg_path)
                tracker.read.add(cfg_path.resolve())

    def load(self, source: Path):
        """Load a configuration file and update the config with its contents.

        Parameters
        ----------
        source
            The path to the configuration file.

        """
        with source.open("rb") as f:
            self.update(tomllib.load(f))

    def update(self, new_settings: Mapping[str, Mapping[str, Any]]):
        """Update the configuration.

        Parameters
        ----------
        new_settings
            The new settings to update the configuration with. The keys should
            correspond to the configuration settings, and the values are a mapping of
            key to new value. Any sections or keys not included will remain at their
            current value.

        """
        # Check if there are sections we don't use.
        extra = set(new_settings.keys()).difference(self.__annotations__)
        if extra:
            warnings.warn(
                f"unknown sections in configuration: {', '.join(extra)}", stacklevel=2
            )

        # Process each section we know about.
        for name, definition in self.__annotations__.items():
            if name not in new_settings:
                continue

            # We don't validate the Matplotlib rcparams.
            if name == "rcparams":
                self.rcparams.update(new_settings["rcparams"])
                continue

            # Load the current and new sections for ease of use.
            section = getattr(self, name)
            new_section = new_settings[name]

            # Check for keys not in the definition of this section.
            extra = set(new_section.keys()).difference(definition.__annotations__)
            if extra:
                warnings.warn(
                    f"unknown settings in section {name}: {', '.join(extra)}",
                    stacklevel=2,
                )

            # And process each key.
            for key, typehint in definition.__annotations__.items():
                if key not in new_section:
                    continue
                val = new_section[key]

                # For subscripted typehints, e.g., list[Path] or Literal[...], we need
                # to split out the base typehint and the contents.
                origin = get_origin(typehint)
                args = get_args(typehint)

                # For basic types, attempt to parse and complain on failure.
                if typehint is Color:
                    try:
                        section[key] = parse_color(val)
                    except ColorError as e:
                        raise ConfigError(name, key, str(e)) from None

                elif typehint is Dimension:
                    try:
                        section[key] = parse_dimension(val)
                    except DimensionError as e:
                        raise ConfigError(name, key, str(e)) from None

                elif typehint is float:
                    try:
                        section[key] = float(val)
                    except ValueError as e:
                        raise ConfigError(name, key, str(e)) from None

                elif typehint is int:
                    try:
                        section[key] = int(val)
                    except ValueError as e:
                        raise ConfigError(name, key, str(e)) from None

                # For a literal, check the value is one of the allowed options.
                elif origin is Literal:
                    if val not in args:
                        raise ConfigError(
                            name,
                            key,
                            f"allowed values are {', '.join(args)} (got {val})",
                        )
                    section[key] = val

                # Assume a string.
                else:
                    section[key] = val


config = Config()


def in_tracking_dir(type, fn):
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
        True if the file is in one of the corresponding tracking directories
        specified in the configuration.

    """
    if type == "data":
        paths = config.paths["data"].strip().splitlines()
    elif type == "import":
        paths = config.paths["pythonpath"].strip().splitlines()
        paths.extend(config.paths["extra_imports"].strip().splitlines())
    else:
        raise ValueError(f"Unknown tracking type {type}.")

    # If we can compute a relative path, it must be within the directory.
    fn = Path(fn).resolve()
    for path in paths:
        resolved = Path(path).resolve()
        try:
            fn.relative_to(resolved)
        except ValueError:
            continue
        return True

    # Not in any of the directories.
    return False


def _relative_if_subdir(fn):
    """Internal: get a relative or absolute path as appropriate.

    Parameters
    ----------
    fn : path-like
        A path to convert.

    Returns
    -------
    fn : str
        A relative path if the file is underneath the top-level project directory, or an
        absolute path otherwise.

    """
    fn = Path(fn).resolve()
    try:
        return fn.relative_to(Path.cwd())
    except ValueError:
        return fn


def _install_extra_file_trackers(trackers: list[str]):
    """Internal: install requested extra file trackers.

    Parameters
    ----------
    trackers : list
        List of strings containing the names of the extra trackers to install. Names are
        not case-sensitive. Currently only "netCDF4" is supported.

    """
    for tracker_name in trackers:
        tracker_name = tracker_name.strip().lower()

        # netCDF4 data storage.
        if tracker_name == "netcdf4":
            import netCDF4

            # Wrap the Dataset class to modify its initialiser to track read files. The
            # class is part of the compiled extension so we can't just override the
            # initialiser.
            class PgfutilsTrackedDataset(netCDF4.Dataset):
                def __init__(self, filename, mode="r", **kwargs):
                    super().__init__(filename, mode=mode, **kwargs)
                    if mode == "r":
                        tracker.read.add(Path(filename).resolve())

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
                        tracker.read.add(Path(fn).resolve())

            netCDF4.MFDataset = PgfutilsTrackedMFDataset

        else:
            raise ValueError(f"Unknown extra tracker {tracker_name}.")


# If the script has been run in an interactive mode (currently, if it is running under
# IPython in a mode with an event loop) then we will display the figure in the save()
# call rather than saving it.  Interactivity is tested each time setup_figure() is
# called. This global stores the latest result to avoid running the test twice (we need
# it in setup_figure() to avoid setting the backend if interactive, and then in save()).
_interactive = False


def setup_figure(
    width: float | str = 1.0,
    height: float | str = 1.0,
    columns: int | None = None,
    margin: bool = False,
    full_width: bool = False,
    **kwargs,
):
    """Set up matplotlib figures for PGF output.

    This function should be imported and run before you import any matplotlib code.
    Figure properties can be passed in as keyword arguments to override the project
    configuration.

    Parameters
    ----------
    width, height
        If a float, the fraction of the corresponding text width or height that the
        figure should take up. If a string, a dimension in centimetres (cm), millimetres
        (mm), inches (in) or points (pt). For example, '3in' or '2.5 cm'.
    columns
        The number of columns the figure should span. This should be between 1 and the
        total number of columns in the document (as specified in the configuration). A
        value of None corresponds to spanning all columns.
    margin
        If True, a margin figure (i.e., one to fit within the margin notes in the
        document) is generated. If the width is a fraction, it is treated as a fraction
        of the marginpar_width configuration setting. The height is still treated as a
        fraction of the text height. The columns setting is ignored if this is True.
    full_width
        If True, a full-width figure, i.e., one spanning the main text, the margin
        notes, and the separator between them, is generated. A fractional width is
        treated relative to the full width. The height is still treated as a fraction of
        the text height. The columns and margin parameters are ignored if this is True.

    """
    global _interactive

    # And anything given in the function call.
    if kwargs:
        config.update({"pgfutils": kwargs})

    # Set environment variables specified in the configuration.
    for line in config.pgfutils["environment"].splitlines():
        line = line.strip()
        if not line:
            continue

        # Check the variables are formatted correctly.
        if "=" not in line:
            raise ValueError(
                "Environment variables should be in the form NAME=VALUE. "
                f"The line '{line}' does not match this."
            )

        # And set them.
        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip()

    # Install extra file trackers if desired.
    extra = config.pgfutils["extra_tracking"].strip()
    if extra:
        _install_extra_file_trackers(extra.split(","))

    # Reset our interactive flag on each call.
    _interactive = False

    # If we're running under IPython, see if there is an event loop in use.
    # Unfortunately, the matplotlib.rcParams['interactive'] (or equivalently,
    # matplotlib.is_interactive()) don't appear to propagate when IPython runs a script
    # so we can't test those.
    try:
        ipython = get_ipython()  # type:ignore[name-defined]
    except NameError:
        pass
    else:
        if ipython.active_eventloop is not None:  # pragma: no cover
            _interactive = True

    # Add any desired entries to sys.path.
    for newpath in config.paths["pythonpath"].splitlines():
        newpath = newpath.strip()
        if newpath:
            sys.path.insert(0, newpath)

    # Set the backend. We don't want to overwrite the current backend if this is an
    # interactive run as the PGF backend does not implement a GUI.
    if not _interactive:  # pragma: no cover
        matplotlib.use("pgf")

    # Specify which TeX engine we are using.
    matplotlib.rcParams["pgf.texsystem"] = config.tex["engine"]

    # Custom TeX preamble.
    preamble = config.pgfutils["preamble"]
    if config.pgfutils["preamble_substitute"]:
        preamble = string.Template(preamble).substitute(basedir=str(Path.cwd()))
    matplotlib.rcParams["pgf.preamble"] = preamble

    # Clear the existing lists of specific font names.
    matplotlib.rcParams["font.sans-serif"] = []
    matplotlib.rcParams["font.serif"] = []
    matplotlib.rcParams["font.cursive"] = []
    matplotlib.rcParams["font.monospace"] = []
    matplotlib.rcParams["font.fantasy"] = []

    # Don't let the backend try to load fonts.
    matplotlib.rcParams["pgf.rcfonts"] = False

    # Set the font family in use.
    matplotlib.rcParams["font.family"] = config.pgfutils["font_family"]

    # If a specific font was given, add it to the list of fonts for
    # the chosen font family.
    if config.pgfutils["font_name"]:
        k = f"font.{config.pgfutils['font_family']}"
        matplotlib.rcParams[k].append(config.pgfutils["font_name"])

    # Set the font sizes.
    matplotlib.rcParams["font.size"] = config.pgfutils["font_size"]
    matplotlib.rcParams["legend.fontsize"] = config.pgfutils["legend_font_size"]

    # Don't use Unicode in the figures. If this is not disabled, the PGF backend can
    # replace some characters with unicode variants, and these don't always play nicely
    # with some TeX engines and/or fonts.
    matplotlib.rcParams["axes.unicode_minus"] = False

    # Line widths.
    matplotlib.rcParams["axes.linewidth"] = config.pgfutils["axes_line_width"]
    matplotlib.rcParams["lines.linewidth"] = config.pgfutils["line_width"]

    # Colours.
    matplotlib.rcParams["figure.facecolor"] = config.pgfutils["figure_background"]
    matplotlib.rcParams["savefig.facecolor"] = config.pgfutils["figure_background"]
    matplotlib.rcParams["axes.facecolor"] = config.pgfutils["axes_background"]

    # Now we need to figure out the total width available for the figure, i.e., the
    # width corresponding to the figure parameter being 1.  First, look up some document
    # properties.
    text_width = config.tex["text_width"]
    margin_width = config.tex["marginpar_width"]
    margin_sep = config.tex["marginpar_sep"]
    num_columns = config.tex["num_columns"]

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
        raise ValueError(
            f"document has {num_columns} columns, but you asked for a figure spanning "
            f"{columns} columns"
        )

    # Not sure what this would mean.
    elif columns < 1:
        raise ValueError("number of columns must be at least one")

    # A number of columns less than the total.
    else:
        # Figure out the width of each column. N columns have N - 1 separators between
        # them.
        columnsep = config.tex["columnsep"]
        total_columnsep = columnsep * (num_columns - 1)
        total_columnw = text_width - total_columnsep
        column_width = total_columnw / num_columns

        # And the width (including the separators between them) of the requested number
        # of columns.
        available_width = (column_width * columns) + (columnsep * (columns - 1))

    # And now we can calculate the actual figure width. If it is a float, it is a
    # fraction of the total available width.  Otherwise, assume it's an explicit
    # dimension.
    try:
        w = float(width)
    except ValueError:
        w = parse_dimension(width)
    else:
        w *= available_width

    # And the figure height.
    try:
        h = float(height)
    except ValueError:
        h = parse_dimension(height)
    else:
        h *= config.tex["text_height"]

    # Set the figure size.
    matplotlib.rcParams["figure.figsize"] = [w, h]

    # Ask for a tight layout (i.e., minimal padding).
    matplotlib.rcParams["figure.autolayout"] = True

    # Copy any specific rcParams the user set.
    matplotlib.rcParams.update(config.rcparams)


def save(figure=None):
    """Save the figure.

    The filename is based on the name of the script which calls this function. For
    example, if you call save() from a script named sine.py, then the saved figure will
    be sine.pgf.

    Parameters
    ----------
    figure: matplotlib Figure object, optional
        If not given, then the current figure as returned by matplotlib.pyplot.gcf()
        will be saved.

    """
    global _interactive

    from matplotlib import __version__ as mpl_version, pyplot as plt

    # Get the current figure if needed.
    if figure is None:
        figure = plt.gcf()

    # Go through and fix up a few little quirks on the axes within this figure.
    for axes in figure.get_axes():
        # There are no rcParams for the legend properties. Go through and set these
        # directly before we save.
        legend = axes.get_legend()
        if legend:
            frame = legend.get_frame()
            frame.set_linewidth(config.pgfutils["legend_border_width"])
            frame.set_alpha(config.pgfutils["legend_opacity"])
            frame.set_ec(config.pgfutils["legend_border_color"])
            frame.set_fc(config.pgfutils["legend_background"])

        # Some PDF viewers show white lines through vector colorbars. This is a bug in
        # the viewers, but can be worked around by forcing the edge of the patches in
        # the colorbar to have the same colour as their faces.  This doesn't work with
        # partially transparent (alpha < 1) images. As of matplotlib v1.5.0, colorbars
        # with many patches (> 50 by default) are rasterized and included as PNGs so
        # this workaround is not needed in most cases.
        #
        # http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.colorbar
        # https://github.com/matplotlib/matplotlib/issues/1188
        # https://github.com/matplotlib/matplotlib/pull/4481
        # https://github.com/matplotlib/matplotlib/commit/854f74a

        # Gather a set of colorbars.  This includes colorbars from images (imshow etc),
        # collections (e.g., scatter plots), and contour plot lines (the roundabout
        # _current_image way -- there doesn't appear to be any other reference from the
        # axes to the QuadContourSet object).
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
            cb.solids.set_edgecolor("face")

    # Interactive mode: show the figure rather than saving.
    if _interactive:  # pragma: no cover
        plt.show()
        return

    # Look at the next frame up for the name of the calling script.
    script = Path(inspect.getfile(sys._getframe(1)))

    # The initial Matplotlib output file, and the final figure file.
    mpname = script.with_suffix(".pgf")
    figname = script.with_suffix(".pypgf")

    # Get Matplotlib to save it.
    figure.savefig(mpname)

    # We want to output tracked files.
    if "PGFUTILS_TRACK_FILES" in os.environ:
        files = []

        # Include imported files if in the tracked directories.
        for fn in tracker.imported:
            if in_tracking_dir("import", fn):
                files.append(f"r:{_relative_if_subdir(fn)}")

        # Include read files if in a tracked directory.
        for fn in tracker.read:
            if in_tracking_dir("data", fn):
                files.append(f"r:{_relative_if_subdir(fn)}")

        # Include all dependencies explicitly added by the script.
        for fn in tracker.explicit_dependencies:
            files.append(f"r:{_relative_if_subdir(fn)}")

        # Include files that were written if they match the pattern used by the PGF
        # backend for rasterised parts of the figures.
        for fn in tracker.written:
            if re.match(r"^.+-img\d+.png$", fn.name):
                files.append(f"w:{_relative_if_subdir(fn)}")

        filestr = "\n".join(files)

        # Figure out where to print it.
        dest = os.environ.get("PGFUTILS_TRACK_FILES") or "1"

        # stdout.
        if dest == "1":
            sys.stdout.write(filestr)

        # stderr.
        elif dest == "2":
            sys.stderr.write(filestr)

        # A named file.
        else:
            with open(dest, "w") as f:
                f.write(filestr)

    # List of all postprocessing functions we are running on this figure. Each should
    # take in a single line as a string, and return the line with any required
    # modifications.
    pp_funcs = []

    # Local cache of postprocessing options.
    fix_raster_paths = config.post_processing["fix_raster_paths"]
    tikzpicture = config.post_processing["tikzpicture"]

    # Add the appropriate directory prefix to all raster images
    # included via \pgfimage.
    if fix_raster_paths:
        figdir = figname.parent

        # Only apply this if the figure is not in the top-level directory.
        if not figdir.samefile("."):
            prefix = figdir.relative_to(Path.cwd())
            expr = re.compile(r"(\\(?:pgfimage|includegraphics)(?:\[.+?\])?{)(.+?)}")
            repl = rf"\1{prefix}/\2}}"
            pp_funcs.append(lambda s: re.sub(expr, repl, s))

    # Use the tikzpicture environment rather than pgfpicture.
    if tikzpicture:
        expr = re.compile(r"\\(begin|end){pgfpicture}")
        repl = r"\\\1{tikzpicture}"
        pp_funcs.append(lambda s: re.sub(expr, repl, s))

    # Postprocess the figure, moving it into the final destination.
    with open(mpname, "r") as infile, open(figname, "w") as outfile:
        # Make some modifications to the header.
        line = infile.readline()
        while line[0] == "%":
            # Update the creator line to include pgfutils version, and add a line with
            # the path of the script that created the figure.
            if "Creator:" in line:
                outfile.write(line[:-1])
                outfile.write(" v")
                outfile.write(mpl_version)
                outfile.write(", matplotlib-pgfutils v")
                outfile.write(__version__)
                outfile.write("\n%%  Script: ")
                outfile.write(str(script.resolve()))
                outfile.write("\n")

            # Update the \input instructions.
            elif r"\input{<filename>.pgf}" in line:
                outfile.write("%%   \\input{")
                outfile.write(str(figname))
                outfile.write("}\n")

            # If we're changing the figure to use the tikzpicture environment, we also
            # need to update the required package.
            elif tikzpicture and r"\usepackage{pgf}" in line:
                outfile.write("%%    \\usepackage{tikz}\n")

            # If we're fixing the paths to rasterised images, we can remove the
            # instructions about using the import package.
            elif fix_raster_paths and line.startswith(
                "%% Figures using additional raster"
            ):
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
