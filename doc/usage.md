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
and 40% of the `\textheight` (see the [configuration documentation](config.md)
for details of how to configure the height and width of your document). The
width and height can also be set to specific sizes:

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
per-figure basis using the `preamble` keyword argument:

```python
from pgfutils import setup_figure, save
setup_figure(width=0.5, height=0.4, preamble="\\usepackage{fontspec}\n\\setmainfont{Noto Sans}")
```


Multiple column support
-----------------------

Having multiple columns in a document is common, and pgfutils supports
generating images which span any number of columns in your document. Suppose
you have [configured pgfutils](config.md) telling it you have a document with a
total text width of 8 inches made up of three columns each separated by 1 inch.
You can now ask for a one column figure,

```python
setup_figure(width=1, height=0.4, columns=1)
```

and the resulting figure will be 2 inches wide (three columns of two inches
plus two separators of one inch each makes up the total text width). If you ask
for two columns,

```python
setup_figure(width=1, height=0.4, columns=2)
```

you get a figure which is 5 inches wide (two columns plus the separator between
them). If you request three columns, the figure will be 8 inches wide. You can
also set columns to `None` (which is the default value) to have the figure span
the entire text width. Any value less than one or greater than the total number
of columns results in an error.

If you use a fractional width, this is relative to the space available for the
number of columns. Taking the second example and asking for 80% of the space,

```python
setup_figure(width=0.8, height=0.4, columns=2)
```

now results in a 4 inch wide figure (i.e., 80% of the 5 inches that would make
up a full two columns).


Saving
------

The figure is saved with a call to the `save()` function. By default, the
current figure (as returned by the `matplotlib.pyplot.gcf()` function) is
saved. This should be sufficient for the vast majority of cases. In the event
that you need to save a particular figure object, pass it to the function:
`save(fig)`.

The filename for the output figure is automatically generated as the name of
the script with the extension replaced with '.pypgf'. For example, in a script
called `magnitude_stats.py`, calling `save()` will generate a figure named
`magnitude_stats.pypgf`.
