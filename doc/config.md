<!--
SPDX-FileCopyrightText: Blair Bonnett
SPDX-License-Identifier: BSD-3-Clause
-->

# Configuration

Primary configuration is done through a configuration file. This should be named
`pgfutils.toml` and placed in the top-level directory, i.e., where you run the scripts
from. An example configuration file containing the default settings is available in the
`data/share/matplotlib-pgfutils/` directory of the source code, or can be viewed [on the
GitHub repository][example_cfg].

The configuration file uses the [TOML][] format. It consists of four sections:

* `tex`: contains details of the TeX setup you are plotting for.
* `pgfutils`: configuration options for the pgfutils module itself.
* `rcParams`: Options to set in Matplotlib's `rcParams` configuration.
* `postprocessing`: Enable or disable various postprocessing options.

The following sections detail use of these sections and the keys they can
contain.

Per-figure configuration can be done in the `setup_figure()` call in the
script. Any of the keys in the `tex`, `pgfutils`, or `postprocessing` sections
can be given as keyword arguments. Options given through this call override
those in the configuration file.

[example_cfg]: https://github.com/bcbnz/matplotlib-pgfutils/blob/main/data/share/matplotlib-pgfutils/pgfutils.toml
[TOML]: https://toml.io


## Specifying values

Many of the configuration options use data types directly supported by TOML (strings,
numbers, boolean values). To set dimensions and colours, the following methods may be
used.

### Dimensions

Matplotlib uses inches for dimensions. If you configure a dimension without a unit
(i.e., as a float) then it will be assumed that it is in inches. To use a different
unit, specify the value as a string with the unit includes, for example `6cm` or `133.2
pt`. The available units are:

* `cm`, `centimetre`, `centimeter`, `centimetres`, or `centimeters`
* `mm`, `millimetre`, `millimeter`, `millimetres`, or `millimeters`
* `in`, `inch`, or `inches`
* `pt`, `point` or `points`

Note that the [points] unit corresponds to the TeX definition of 1/72.27 of an inch.
This allows you to specify dimensions in the same units as TeX. The postscript point (or
desktop publishing point) is slightly different at 1/72 of an inch.

[points]: https://en.wikipedia.org/wiki/Point_(typography)


### Colours

The following options may be used to define a colour:

* The strings `none` or `transparent`.
* A string with one of [Matplotlib's named colours][mpl-named].
* A single floating-point value between 0 and 1 giving a greyscale level.
* A tuple of three floating-point values, `(r, g, b)`. These values must be between 0
  and 1 and represent the fraction of each primary colour. The resulting colour has 100%
  opacity.
* A tuple of four floating-point values, `(r, g, b, a)`. These values must be between 0
  and 1. The first three values represent the fraction of each primary colour, and the
  final value gives the opacity.

[mpl-named]: https://matplotlib.org/stable/gallery/color/named_colors.html


## TeX settings

The `tex` section of the configuration defines the properties of the TeX document that
figures are being generated for. The default settings for the section are:

```toml
--8<-- "doc/config_defaults_tex.toml"
```

When generating PGF code, the backend uses the given engine to measure strings so it
knows the correct location to place them. The `engine` setting can be one of the
strings `xelatex`, `pdflatex` or `lualatex`.


### Page layout

The next set of settings correspond to the layout of the page. The default values are
taken from an XeLaTeX document using the article class with its standard layout. The
dimensions of a TeX document can be measured using the [layouts][] package:

```tex
\documentclass{article}

\usepackage{layouts}

\begin{document}

\begin{figure}
  \currentpage\pagedesign
\end{figure}

\end{document}
```

When compiled, this prints a diagram in the output document showing the dimensions.

The `text_width` and `text_height` settings give the size of the main text area of the
document. The `marginpar_width` and `marginpar_sep` refer to the width of the margin
notes and the separator between the main text area and the margin notes. They are used
when generating figures which fit in the margin notes, or which span the main text area
and the margin notes.

The number of columns and the width of the separators between them are only used when
generating figures for multiple-column documents.

[layouts]: https://ctan.org/pkg/layouts


### Preamble

In order to place labels etc. accurately, the `pgf` backend calls the specified TeX
engine to measure their height and width. This means that if you have setup custom fonts
etc. in your TeX document preamble, the backend must also set them up before trying to
measure labels.

A TeX preamble can be specified as a string given to the `preamble` key. This does not
have to specify the entire preamble for your main document, just the portions relevant
for setting up the fonts the figures will use.

```toml
[tex]
preamble='\usepackage{fontspec}\setmainfont{Noto Sans}'
```

Note that this uses single quotes around the string; in TOML terms these are *literal
strings* which don't treat the slashes in the TeX macro as escape characters. For
readability, a multi-line literal string can also be used:

```toml
[tex]
preamble='''
  \usepackage{fontspec}
  \setmainfont{Noto Sans}
'''
```

Note that the `pgf` backend runs TeX in a temporary directory. Hence, any paths
(for example, to a custom font) must be given as absolute paths. To simplify
this configuration, pgfutils can perform path substitution in the preamble. If
the `preamble_substitute` option is enabled, then any reference to `$basedir`
or `${basedir}` in the preamble will be replaced by the absolute path to the
base directory. This is the top-level directory the script is run from, i.e.,
the one which contains the configuration file. For example:

```toml
[tex]
preamble_substitute = true
preamble = '''
  \usepackage{fontspec}
  \setmainfont[
    Path           = ${basedir}/fonts/,
    Extension      = .ttf,
    UprightFont    = *-Regular,
    BoldFont       = *-Bold,
    BoldItalicFont = *-BoldItalic
  ]{MyCustomFontName}
'''

[pgfutils]
font_family = "serif"
font_name = "MyCustomFontName"
```

Note that `preamble_substitute` is off by default, i.e., it must be explicitly
enabled if you want to use it.


## pgfutils options

The `pgfutils` section configures the settings for figures generated by pgfutils. The
default values for this section are:

```toml
--8<-- "doc/config_defaults_pgfutils.toml"
```

### Background colours

The general background of the figure is set by the `figure_background` option. The
background of the axes in the figure is set by `axes_background`. The default is to have
the figure background transparent so it fits into the final document and the axes
background white to provide contrast for the plots.


### Font settings

The general font family (`serif`, `sans-serif`, `monospace` or `cursive`) is
set by the `font_family` parameter. With no other configuration, the default
TeX font for this family will be used. To specify a particular font, give the
name in the `font_name` setting. If this requires a particular setup to import
it, use the [preamble configuration](#preamble) to do so. Two font sizes can be set:
`font_size` is the general font size for the figure, and `legend_font_size` is
the size of the text in any legends in the figure.


### Line widths

The width of the lines used to plot data is set by `line_width`. The
`axes_line_width` property controls the width of the line used to draw the
axes.


### Legends

In addition to the font size (`legend_font_size` as mentioned above), the width
and color of the border around the legend (`legend_border_width` and
`legend_border_color` respectively) and the color of the background
(`legend_background`) can be set. The opacity of both the border and the
background is controlled by the `legend_opacity` setting, which should be a
float between 0 (transparent) and 1 (solid). Note that, due to the way
Matplotlib processes the legend, any opacities set in the border or background
colors is overridden by this value.

If enabled, the `separate_legend` setting causes pgfutils to extract any legends from
the figures it saves and write them to separate files. This allows you to place them
elsewhere in your document, for example in the margins. It may be preferable to keep
this disabled in the configuration file, and enable it on a per-figure basis when
calling `setup_figure`.


### Extra tracking

This is a comma-separated list of extra libraries to install file tracking on.
See the [file tracking](file_tracking.md) documentation for more details.


### Environment variables

Environment variables to set can be specified using the multi-line option
``environment``. Each line represents one environment variable in the format
``name = value``:

```toml
[pgfutils]
environment = '''
  name1 = "value1"
  name2 = "value2"
'''
```

Existing environment variables of the same name will be overwritten. This means that if
you specify the same variable multiple times the last value will be used. For example,
the configuration

```toml
[pgfutils]
environment = '''
  name1 = "value1"
  name2 = "value2"
  name1 = "value3"
'''
```

will result in `name1` being set to `value3`. The variables are set during the call to
`setup_figure()`, so any libraries that read the environment variables must be imported
after this call.

Note that the `PGFUTILS_TRACK_FILES` variable described in the [file tracking
documentation](file_tracking.md) can be configured through this option, for example to
output tracked files to stdout:

```toml
[pgfutils]
environment = '''
  PGFUTILS_TRACK_FILES = "1"
'''
```


## Path settings

The [file tracking](file_tracking.md) code checks any file opened for reading to see if
it is a dependency. If it is in one of the directories given under the `data` key, or in
any subdirectory of one of these directories, then it is counted as a dependency. The
top-level directory (the directory the script was run from) is always included as a data
directory, so you only need to specify directories outside the top-level directory.
Multiple entries must be specified on separate lines of the configuration.

```toml
[paths]
data = '''
  /data/common
'''
```

Note that these directories are not added to any kind of search path, so any
code which uses them still has to give a complete path.

If you have Python code in other libraries you want to be able to import in
your scripts, you can use the `pythonpath` option in the `paths` section of the
configuration file to specify custom search paths for Python. This is a
multi-line entry with one path per line.  The paths are inserted at the start
of `sys.path` when you call `setup_figure()`. They are inserted in the order
given in the configuration, which means the last path in the configuration will
be the first entry in `sys.path`. They are not modified or checked in any way.
Relative paths will therefore be interpreted by Python as being relative to the
directory it was run from, which should be the top-level directory of your
project.

```toml
[paths]
pythonpath = '''
  pythonlib/
  /usr/share/myotherlib
'''
```

Python imports can also be handled by the [file tracking](file_tracking.md). If
enabled, any library imported from a directory (or subdirectory) specified in
the `pythonpath` option is treated as a dependency and output as part of the
file tracking details. If you have other libraries which are already in the
Python path which you want to be tracked as dependencies, you can add the
appropriate directories to the `extra_imports` option:

```toml
[paths]
extra_imports = '''
   /home/username/.local/lib/
'''
```


Matplotlib rcParams
-------------------

Matplotlib can be customised using its [rcParams][] system (this is how pgfutils does
much of its setup). If you want to override rcParams settings, you can specify them in
the `rcParams` section:

```toml
[rcParams]
"figure.facecolor" = "blue"
"xtick.labelsize" = 8
```

Generally you should do this through Matplotlib itself, i.e., with a
`matplotlibrc` file. The ability to set them in pgfutils is intended to be
used if it overrides an rcParams setting that you want to change back.

Note that these rcParams are applied after all other figure configuration is
complete. This means that they will completely override pgfutils. For example,
the configuration given above would result in the figure background being blue,
regardless of what you specify `figure_background` as in `pgfutils.toml` options
or the `setup_figure()` call.

[rcParams]: https://matplotlib.org/users/customizing.html


## Post-processing

pgfutils can perform some postprocessing on the generated figure. The default
settings are:

```toml
--8<-- "doc/config_defaults_post_processing.toml"
```


### `fix_raster_paths`

The PGF backend has no knowledge of the directory structure. When creating a rasterized
image to include in the figure (e.g., a PNG image of an array you've used `imshow` on),
it assumes the figure will be in the same directory as the main TeX file. Accordingly,
the image is included using `\pgfimage{name.png}`.  If you have your figures in a
separate directory such as `figures/`, inputting the figure will fail. There are TeX
packages which can work around this, but it is probably simpler to let pgfutils take
care of it. If the `fix_raster_paths` postprocessing option is enabled, any calls to
`\pgfimage` or `\includegraphics` will be updated to include the relative directory of
the figure. For this to work, the script **must** be run from the same directory as your
top-level TeX file.


### `tikzpicture`

The PGF backend creates the figure within a `pgfpicture` environment. Although
this is fine most of the time, the TikZ external library (which 'externalises'
TikZ images to PDF to reduce compilation time) requires the `tikzpicture`
environment. Enabling this postprocessing option will change the environment
used for the figure to `tikzpicture`. Note that it does not change any of the
drawing commands. As TikZ is a superset of PGF, this should work in most cases,
although errors may occur in some figures.
