Usage
=====

Using pgfutils generally requires three extra lines to be added to your
plotting code: an import and a setup call at the start of the script, and a
save call at the end.

Setup
-----

The figure setup should be done at the very start of the script, and definitely
before importing Matplotlib, NumPy, or anything which internally imports either
of them. Some of the internal configuration relies on being the first to import
these modules.

A basic example of figure setup is:

```python
from pgfutils import setup_figure, save
setup_figure(width=0.6, height=0.4)
```

This sets the figure to take up 60% of the `\textwidth` of the TeX document,
and 40% of the `\textheight` (see [Config](config.md) for details of how to
configure the height and width of your document). The width and height can also
be set to specific sizes:

```python
from pgfutils import setup_figure, save
setup_figure(width='7.5cm', height='2in')
```

Available units are 'cm', 'mm', 'in', and 'pt. These two methods can be mixed,
i.e., one dimension can be a fraction of the document size, and the other can
be explicitly set:

```python
from pgfutils import setup_figure, save
setup_figure(width='80mm', height=0.4)
```

The project-wide configuration can be overridden by using keyword arguments.
For example, to set the background color of a figure:

```python
from pgfutils import setup_figure, save
setup_figure(width=0.95, height=0.3, figure_color='yellow')
```

This particular example is useful for showing the extent of the final figure in
order to determine whether unnecessary whitespace is being introduced by
Matplotlib or TeX.

The preamble used for measuring label widths etc. can also be overridden on a
per-figure basis using the `preamble` keyword argument. As with the
configuration file, this can be given either as a string:

```python
from pgfutils import setup_figure, save
setup_figure(width=0.5, height=0.4, preamble="\\usepackage{fontspec}\n\\setmainfont{Noto Sans}")
```

or as a list of lines:

```python
from pgfutils import setup_figure, save
setup_figure(width=0.5, height=0.4, preamble=[r"\usepackage{fontspec}", r"\setmainfont{Noto Sans}"])
```


Saving
------

The figure is saved with a call to the `save()` function. By default, the
current figure (as returned by the `matplotlib.pyplot.gcf()` function) is
saved. This should be sufficient for the vast majority of cases. In the event
that you need to save a particular figure object, pass it to the function:
`save(fig)`.

The filename for the output figure is automatically generated as the name of
the script with the extension replaced with '.pypgf'. For example, in a script
called 'magnitude_stats.py', calling `save()` will generate a figure named
`magnitude_stats.pypgf`.
