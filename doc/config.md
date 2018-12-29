Configuration
=============

Primary configuration is done through a configuration file. This should be
named `pgfutils.cfg` and placed in the top-level directory, i.e., where you run
the scripts from. The configuration file is in [JSON format][1], and should
consist of one object (in Python terms, a dictionary). Any combination of four
items can be present:

* `pgfutils`: Configuration options for the pgfutils module.
* `rcParams`: Options to set in Matplotlib's `rcParams` configuration.
* `preamble`: The TeX preamble to use when measuring string widths etc.
* `postprocessing`: Enable or disable various postprocessing options.

The following sections detail use of these items.

Per-figure configuration can be done in the `setup_figure()` call in the
script. Each of the `pgfutils` options can be given as keyword arguments, and
the TeX preamble and postprocessing options can also be passed in using the
`preamble` and `postprocessing` keywords respectively.  Options
given through this call override those in the configuration file.


pgfutils options
----------------

The default values of the `pgfutils` options are equivalent to the following
configuration:

```json
{
  "pgfutils": {
    "engine": "xelatex",
    "text_height": 7.63,
    "text_width": 4.79,
    "font_family": "serif",
    "font_name": null,
    "font_size": 10,
    "legend_font_size": 10,
    "line_width": 1,
    "axes_line_width": 0.6,
    "figure_color": null,
    "axes_color": "white",
}
```

Dimensions can be given as floats (in which case they are in inches,
Matplotlib's unit of choice) or as strings with a unit attached: "in" for
inches, "cm" for centimetres, "mm" for millimetres, or "pt" for points. Font
and line sizes are given in points. Colours can be given as named strings,
`(r, g, b)` or `(r, g, b, a)` tuples, a float for a greyscale fractions, or
`None`/`null` for transparent.


### TeX settings

The PGF backend can use one of three TeX engines to measure strings etc:
`xelatex`, `pdflatex` or `lualatex`. This is specified in the `engine` setting.
The width and height of the text area in the document are given in the
`text_width` and `text_height` values, with the default values being taken from
a `xelatex` document using the article class with no adjust of margins etc. The
dimensions of a TeX document can be measured using the `layout` package:

```tex
\documentclass{article}

\usepackage{layout}
\begin{document}

\layout{}

\end{document}
```

This prints a diagram in the output document showing the dimensions.


### Font settings

The general font family (`serif`, `sans-serif`, `monospace` or `cursive`) is
set by the `font_family` parameter. With no other configuration, the default
TeX font for this family will be used. To specify a particular font, give the
name in the `font_name` setting. If this requires a particular setup to import
it, use the preamble configuration to do so. Two font sizes can be set:
`font_size` is the general font size for the figure, and `legend_font_size` is
the size of the text in any legends in the figure.


### Line widths

The width of the lines used to plot data is set by `line_width`. The
`axes_line_width` property controls the width of the line used to draw the
axes.


### Background colours

The general background of the figure (i.e., of the area outside of any axes in
it) is set by the `figure_color` option. The background of the axes in the
figure is set by `axes_color`.


Matplotlib rcParams
-------------------

Matplotlib can be customised using its [rcParams][2] system (this is how
`pgfutils` sets up figures). If you want to override rcParams settings, you can
specify them in an object under the `rcParams` configuration key:

```json
{
  "rcParams": {
    "figure.facecolor": "blue",
    "xtick.labelsize": 8
  }
}
```

Generally you should do this through Matplotlib itself, i.e., with a
`matplotlibrc` file. The ability to set them in `pgfutils` is intended to be
used if it overrides an `rcParams` setting that you want to change back.

Note that these `rcParams` are applied after all other figure configuration is
complete. This means that they will completely override `pgfutils`. For
example, the configuration given above would result in the figure background
being blue, regardless of what you specify `figure_color` as in the `pgfutils`
options or the `setup_figure()` call.


TeX preamble
------------

In order to place labels etc. accurately, the `pgf` backend calls the specified
TeX engine to measure their height and width. This means that if you have setup
custom fonts etc. in your TeX document preamble, the backend must also set them
up before trying to measure labels. This can be done using the `preamble` key:

```json
{
  "preamble": "\\usepackage{fontspec}\n\\setmainfont{Noto Sans}"
}
```

For convenience, the preamble can also be specified as an array (list) of lines:

```json
{
  "preamble": [
    "\\usepackage{fontspec}",
    "\\setmainfont{Noto Sans}"
  ]
}
```


Postprocessing
--------------

pgfutils can perform some postprocessing on the generated figure. Each of the
postprocessing options listed below is a Boolean flag.

### `fix_raster_dir` (default True)

The PGF backend has no knowledge of the directory structure. When creating a
rasterized image to include in the figure (e.g., a PNG image of an array you've
used `imshow` on), it assumes the figure will be in the same directory as the
main TeX file. Accordingly, the image is included using `\pgfimage{name.png}`.
If you have your figures in a separate directory such as `figures/`, inputting
the figure will fail. There are TeX packages which can work around this, but it
is probably simpler to let pgfutils take care of it. If the `fix_raster_dir`
postprocessing option is set to True, any calls to `\pgfimage` will be updated
to include the relative directory of the figure.


### `tikzpicture` (default False)

The PGF backend creates the figure within a `pgfpicture` environment. Although
this is fine most of the time, the TikZ external library (which 'externalises'
TikZ images to PDF to reduce compilation time) requires the `tikzpicture`
environment. Enabling this postprocesing option will change the environment
used for the figure to `tikzpicture`. Note that it does not change any of the
drawing commands. As TikZ is a superset of PGF, this should work in most cases,
although errors may occur in some figures.


[1]: https://en.wikipedia.org/wiki/JSON
[2]: https://matplotlib.org/users/customizing.html
