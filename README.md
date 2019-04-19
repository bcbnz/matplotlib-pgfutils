pgfutils
========

The [Portable Graphics Format (PGF)][1] is a language for producing vector
graphics within TeX documents. There is also a higher-level language TikZ (TikZ
ist kein Zeichenprogramm -- TikZ is not a drawing program) which uses PGF.

Since version 1.2, the Python plotting library [Matplotlib][2] has included a
PGF backend to generate figures ready for inclusion in a TeX document. In order
to get consistent figures that fit with the style of the document, this
requires some configuration. The aim of pgfutils is to simplify this
configuration and allow figures to be easily generated from a Python script.

The module provides two functions which set up and then save the figure. The
actual plotting is performed by standard Matplotlib functions. For example, to
generate a plot showing the 1st, 3rd, 5th, 7th, 9th and 11th harmonics of an
ideal square wave and the resulting sum:

```python
# Set up the figure environment.
from pgfutils import setup_figure, save
setup_figure(width=0.9, height=0.4)

import numpy as np
from matplotlib import pyplot as plt

# Generate square wave from a few terms of its Fourier series.
f = 3
t = np.linspace(0, 1, 501)
square = np.zeros(t.shape)
for n in range(1, 12, 2):
    # Create this harmonic and plot it as a dashed
    # partially-transparent line.
    component = np.sin(2 * n * np.pi * f * t) / n
    plt.plot(t, component, '--', alpha=0.4)

    # Add it to the overall signal.
    square += component

# Scale the final sum.
square *= 4 / np.pi

# Plot and label the figure.
plt.plot(t, square, 'C0')
plt.xlim(0, 1)
plt.ylim(-1.2, 1.2)
plt.xlabel("Time (s)")
plt.ylabel("Amplitude (V)")

# Save as a PGF image.
save()
```

[1]: https://sourceforge.net/projects/pgf/
[2]: https://matplotlib.org/


Documentation
-------------

Documentation is available in Markdown format in the doc/ directory:

* [Usage](doc/usage.md)
* [Configuration](doc/config.md)
* [Interactive mode](doc/interactive.md)
* [File tracking](doc/file_tracking.md)
* [Latexmk integration](doc/latexmk.md)

An example configuration file showing the default settings is given in
[extras/pgfutils.cfg](extras/pgfutils.cfg).


Unit testing
------------

[![Build Status](https://travis-ci.com/bcbnz/matplotlib-pgfutils.svg?branch=master)](https://travis-ci.com/bcbnz/matplotlib-pgfutils)
[![codecov](https://codecov.io/gh/bcbnz/matplotlib-pgfutils/branch/master/graph/badge.svg)](https://codecov.io/gh/bcbnz/matplotlib-pgfutils)

Extensive unit tests are included in the tests/ directory of the source. Each
commit to the source repository is automatically tested thanks to [Travis
CI][3]. The test coverage (that is, how many of the lines of code in the source
were executed during the tests) is monitored by [Codecov][4]. The badges above
show the status of the last commit made to the source.

You can also run the tests on a local copy of the code. They are designed to be
run with the [pytest][5] framework and employ the [Coverage.py][6] package via
the [pytest-cov][7] plugin to measure the coverage. If you have these packages
installed, run `pytest` from the top-level directory to execute the tests. A
basic test coverage report will be printed on the terminal, and the full report
can be viewed by opening the `htmlcov/index.html` file in your web browser.

[3]: https://travis-ci.com/bcbnz/matplotlib-pgfutils
[4]: https://codecov.io/gh/bcbnz/matplotlib-pgfutils
[5]: https://pytest.org/
[6]: https://coverage.readthedocs.io/
[7]: https://pytest-cov.readthedocs.io/


License
-------

pgfutils is released under the three-clause BSD license.

The Cotham Sans font used in some unit tests is copyright (c) 2015 Sebastien
Sanfilippo and is licensed under the SIL Open Font License, Version 1.1. The
license can be found in the source at tests/sources/fonts/Cotham/OFL.txt or
online at https://scripts.sil.org/OFL and the font itself can be found at
https://github.com/sebsan/Cotham
