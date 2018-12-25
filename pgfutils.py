# Copyright 2018 Blair Bonnett
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

import inspect
import json
import os
import os.path
import matplotlib
import sys


# The current configuration.
_config = {
    'pgfutils': {
        'engine': 'xelatex',
        'font_family': 'serif',
        'font_name': None,
        'font_size': 10,
        'legend_font_size': 10,
        'line_width': 1,
        'axes_line_width': 0.6,
        'text_width': 4.79,
        'text_height': 7.63,
        'figure_color': 'white',
        'axes_color': 'white',
    },

    'rcParams': {
    },

    'preamble': ''
}

# If the script has been run in an interactive mode (currently, only IPython's
# pylab mode) then we will display the figure in the save() call rather than
# saving it.
# Interactivity is tested each time setup_figure() is called. This global
# stores the latest result to avoid running the test twice (we need it in
# setup_figure() to avoid setting the backend if interactive, and then in
# save()).
_interactive = False


def _config_from_json(fn):
    """Internal: update the configuration from a JSON file.

    Parameters
    ----------
    fn: string
        The filename to load the configuration from.

    """
    # Parse the file.
    with open(fn, 'r') as f:
        opts = json.load(f)

    # Check we have an object at the root of the JSON.
    if not isinstance(opts, dict):
        raise ValueError("JSON configuration must be an object (dictionary).")

    # Pull out the sections.
    pgfopts = opts.pop('pgfutils', {})
    rcParams = opts.pop('rcParams', {})
    preamble = opts.pop('preamble', None)

    # Anything left in the options: unknown section.
    if opts:
        k = opts.keys()
        raise ValueError("Unknown configuration section(s): {}".format(", ".join(k)))

    # Update the config with these options.
    if pgfopts or rcParams or preamble:
        _update_config(pgfopts, rcParams, preamble)


def _update_config(pgfopts, rcParams, preamble):
    """Internal: update the configuration.

    Parameters
    ----------
    pgfopts, rcParams: dictionary
        pgfutils and Matplotlib settings.
    preamble: string or list of strings
        TeX preamble.

    """
    global _config

    # Handle strings.
    for k in {'engine', 'font_family'}:
        v = pgfopts.pop(k, None)
        if v is not None:
            _config['pgfutils'][k] = str(v)

    # Handle strings that can also be None.
    for k in {'font_name',}:
        v = pgfopts.pop(k, -1)
        if v != -1:
            _config['pgfutils'][k] = v

    # Handle colours.
    for k in {'figure_color', 'axes_color'}:
        v = pgfopts.pop(k, None)
        if v is not None:
            _config['pgfutils'][k] = _parse_color(v)

    # Handle dimensions.
    for k in {'text_width', 'text_height'}:
        v = pgfopts.pop(k, None)
        if v is not None:
            _config['pgfutils'][k] = _parse_dimension(v)

    # Handle sizes (fonts, thicknesses etc).
    for k in {'font_size', 'legend_font_size', 'line_width', 'axes_line_width'}:
        v = pgfopts.pop(k, None)
        if v is not None:
            if isinstance(v, (int, float)):
                _config['pgfutils'][k] = v
            else:
                _config['pgfutils'][k] = float(v)

    # Any other option is unknown.
    if pgfopts:
        k = pgfopts.keys()
        raise ValueError("Unknown pgfutils option(s): {}".format(", ".join(k)))

    # Can just copy any specified rcParams over.
    _config['rcParams'].update(rcParams)

    # Save the preamble if one was given.
    # If the preamble is a list, turn it into a string first.
    if preamble is not None:
        if isinstance(preamble, list):
            preamble = '\n'.join(preamble)
        _config['preamble'] = preamble.strip()


def _parse_dimension(dim):
    """Internal: turn a dimension into inches for matplotlib.

    Parameters
    ----------
    dim: string or float
        If a float, it is assumed to be in inches already. Otherwise, the
        dimension as a string '<value><unit>', where unit can be 'cm', 'mm',
        'in', or 'pt'. If a unit is not given, it is assumed to be inches.

    Returns
    -------
    float: The dimension in inches.

    Raises
    ------
    ValueError:
        Unit is unknown, or the value cannot be converted to a float.

    """
    if isinstance(dim, float):
        return dim

    # Break into components.
    dim = dim.strip().lower()
    size, unit = dim[:-2], dim[-2:]

    # Pick out the divisor to convert into inches.
    factor = {
        'cm': 2.54,
        'mm': 25.4,
        'in': 1,
        'pt': 72,
    }.get(unit, None)

    # Unknown unit.
    if factor is None:
        # If the entire input is a float, assume its already in inches.
        try:
            val = float(dim)
        except ValueError:
            raise ValueError("Unknown unit {0:s}.".format(unit))
        return val

    # Do the conversion.
    return float(size) / factor


def _parse_color(value):
    """Internal: check the value can be used as a Matplotlib color.

    Parameters
    ----------
    value: string, float, tuple of floats
        The input color value. Can be a named colour, a tuple (r, g, b), a
        tuple (r, g, b, a), a floating-point value in [0, 1] for grayscale, or
        'none' for transparent.

    Returns
    -------
    matplotlib-compatible colour.

    Raises
    ------
    ValueError
        The value could not be interpreted as a color.

    """
    # Floats: for historical reasons Matplotlib requires this to be a string.
    if isinstance(value, float):
        if not (0 <= value <= 1):
            raise ValueError("Greyscale floats must be in [0, 1].")
        value = str(value)

    # Matplotlib provides a function to check this is valid.
    # Technically, this could do the [0, 1] check above, but this would result
    # in a less obvious error message.
    if not matplotlib.colors.is_color_like(value):
        raise ValueError("{} could not be interpreted as a color.".format(value))

    # Now we know its valid.
    return value


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

    # Load configuration from a JSON file if one exists.
    if os.path.exists('pgfutils.cfg'):
        _config_from_json('pgfutils.cfg')

    # And anything given in the function call.
    preamble = kwargs.pop('preamble', None)
    _update_config(kwargs, {}, preamble)

    # Reset our interactive flag on each call.
    _interactive = False

    # If we're running under IPython, see if it is in pylab mode.
    try:
        ipython = get_ipython()
    except NameError:
        pass
    else:
        for key, val in ipython.config.items():
            if val.get('pylab', '') in {'auto', 'inline'}:
                _interactive = True

    # Set the backend. We don't want to overwrite the current backend if this
    # is an interactive run as the PGF backend does not implement a GUI.
    if not _interactive:
        matplotlib.use('pgf')

    # Specify which TeX engine we are using.
    matplotlib.rcParams['pgf.texsystem'] = _config['pgfutils']['engine']

    # Custom TeX preamble.
    matplotlib.rcParams['pgf.preamble'] = _config['preamble']

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
    matplotlib.rcParams['font.size'] = _config['pgfutils']['font_size']
    matplotlib.rcParams['legend.fontsize'] = _config['pgfutils']['legend_font_size']

    # Don't use Unicode in the figures. If this is not disabled, the PGF
    # backend can replace some characters with unicode variants, and these
    # don't always play nicely with some TeX engines and/or fonts.
    matplotlib.rcParams['axes.unicode_minus'] = False

    # Line widths.
    matplotlib.rcParams['axes.linewidth'] = _config['pgfutils']['axes_line_width']
    matplotlib.rcParams['lines.linewidth'] = _config['pgfutils']['line_width']

    # Colours.
    matplotlib.rcParams['figure.facecolor'] = _config['pgfutils']['figure_color']
    matplotlib.rcParams['savefig.facecolor'] = _config['pgfutils']['figure_color']
    matplotlib.rcParams['axes.facecolor'] = _config['pgfutils']['axes_color']

    # Set the figure size.
    try:
        w = width * float(_config['pgfutils']['text_width'])
    except TypeError:
        w = _parse_dimension(width)
    try:
        h = height * float(_config['pgfutils']['text_height'])
    except TypeError:
        h = _parse_dimension(height)
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
        #
        # So far I've found colorbars from images (imshow etc) and collections
        # (scatter plots and the like).
        for obj in axes.images + axes.collections:
            cb = obj.colorbar
            if not cb:
                continue

            # Ignore rasterized or transparent colorbars.
            # Note that alpha=None is the same as alpha=1.
            if cb.solids.get_rasterized():
                continue
            if (cb.alpha or 1.0) < 1.0:
                continue
            cb.solids.set_edgecolor('face')


    # Interactive mode: show the figure.
    global _interactive
    if _interactive:
        plt.show()

    # Non-interactive: save it.
    else:
        # Look at the next frame up for the name of the calling script.
        name, ext = os.path.splitext(inspect.getfile(sys._getframe(1)))

        # Replace the extension and save.
        figure.savefig(name + ".pgf")
        os.rename(name + ".pgf", name + ".pypgf")
