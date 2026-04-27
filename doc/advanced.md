<!--
SPDX-FileCopyrightText: Blair Bonnett
SPDX-License-Identifier: BSD-3-Clause
-->

# Advanced usage

## Legends in margin

If you set the `separate_legend` option to True (either in the configuration file, or on
a per-figure basis as in this example), then pgfutils will extract all legends from the
figure and save them to separate files, allowing you to place them with TeX. For the
following example, we will create a simple plot with two sinusoids.

```python title="separate_legend.py"
from pgfutils import save, setup_figure

setup_figure(width=1, height=0.2, separate_legend=True)

from matplotlib import pyplot as plt
import numpy as np

# Plot two sine waves.
t = np.arange(0, 1, 2e-3)
s = np.sin(2 * np.pi * 3 * t)
plt.plot(t, s, "-v", label="3 Hz", markevery=30)
s = np.sin(2 * np.pi * 4 * t)
plt.plot(t, s, "-s", label="4Hz", markevery=30)

# Make a legend.
plt.legend()

# And label the plot.
plt.xlabel("Time [s]")
plt.ylabel("Amplitude [V]")
plt.xlim(0, 1)
plt.ylim(0, 1)
plt.yticks([-1, -0.5, 0, 0.5, 1])
plt.grid(True, ls=":")

save()
```

Running `python separate_legend.py` should result in two files being produced:
`separate_legend.pypgf` containing the main plot, and `separate_legend_legend0.pypgf`
containing the legend. If the figure contains multiple legends (such as multiple
sub-plots each having a legend), one file per legend will be produced with increasing
numerical suffixes.

We then need to figure out how to place the legend in the TeX document. If the figures
are floating, then we have to somehow place this once TeX has decide where to place the
figures. The following example uses the [tikzmark][] package to place a marker alongside
the main figure, and then a [shipout hook][] which runs when a page is finalised. This
then places the legend in the margin based on the position of the marker and the
positions provided by the [tikzpagenodes][] package.

```tex title="separate_legend.tex"
\documentclass{book}

\usepackage{lipsum}
\usepackage{tikz}
\usetikzlibrary{tikzmark}
\usepackage{tikzpagenodes}

% Mark and place a legend in the margin aligned to the current spot.
%
% Optional argument: label for the marker. Must be unique within the document.
%   Defaults to the filename of the legend, so you only need to specify this if you use
%   the same legend file multiple times.
%
% Mandatory argument: filename of the legend.
\NewDocumentCommand{\marginlegend}{O{#2}m}{
  % Mark the current location with a reference.
  \tikzmark{#1}

  % Add hook code which runs when each page is shipped.
  \AddToHook{shipout/foreground}[#1]{
    % Wait until we are on the page with the original mark.
    \iftikzmarkoncurrentpage{#1}
      \begin{tikzpicture}[remember picture,overlay]
        % Coordinate where we want the y position of the legend anchor.
        \coordinate (mainfig) at ([yshift=-5mm]pic cs:#1);

        % Coordinate where we want the x position of the legend anchor.
        \coordinate (marginpar) at (current page marginpar area.north);

        % And put a node containing the legend there.
        \node[anchor=north, inner sep=0, outer sep=0] at (marginpar |- mainfig){
          \input{#2}
        };
      \end{tikzpicture}

      % Don't need this hook code anymore.
      \RemoveFromHook{shipout/foreground}[#1]
    \fi
  }
}

\begin{document}

\lipsum[1-5]

\begin{figure}
  \marginlegend{separate_legend_legend0.pypgf}
  \input{separate_legend.pypgf}
  \caption{
    This is a test figure with two sine waves.
  }
\end{figure}

\lipsum[2-6]

\end{document}
```

If you now compile the document (e.g., with `xelatex separate_legend`) then you will see
the main figure is present but there is no legend. As the position of the markers is
written to the auxiliary file, it is not available until the next run (in the same
manner as cross-references or bibliography data). You need to compile multiple times
when the position changes; for an initial build, this will probably require three
compilations. When you no longer get the message

```
LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right.
```

then the position is stabilised. You should now have a document with the legend in the
margin alongside the figure. Build tools like `latexmk` should detect this message and
automatically re-run the appropriate number of times.

Note that you can use any TeX macros to figure out the appropriate alignment. For
example, in a two-sided document you could change the alignment based on whether the
current page is an odd page or even page so that the margin is aligned to the side of
the margin closest to the text (this requires the [ifoddpage][] package):

```tex
% Coordinate where we want the x position of the legend anchor.
\ifoddpage
  \coordinate (marginpar) at (current page marginpar area.west);
\else
  \coordinate (marginpar) at (current page marginpar area.east);
\fi

% And put a node containing the legend there.
\ifoddpage
  \node[anchor=north west, inner sep=0, outer sep=0] at (marginpar |- mainfig){
      \input{#2}
  };
\else
  \node[anchor=north east, inner sep=0, outer sep=0] at (marginpar |- mainfig){
      \input{#2}
  };
\fi
```

[tikzmark]: https://ctan.org/pkg/tikzmark
[shipout hook]: https://www.latex-project.org/help/documentation/ltshipout-doc.pdf
[tikzpagenodes]: https://ctan.org/pkg/tikzpagenodes
[ifoddpage]: https://ctan.org/pkg/ifoddpage
