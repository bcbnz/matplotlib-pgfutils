# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from pgfutils import save, setup_figure

setup_figure(
    width=0.5,
    height=0.4,
    preamble_substitute=True,
    preamble=r"""
        \usepackage{fontspec}
        \setmainfont{CothamSans}[Path=${basedir}/../Cotham/,Extension=.otf]""",
)

from matplotlib import pyplot as plt
import numpy as np

t = np.linspace(-4, 4, 201)
plt.plot(t, 2 * np.sin(2 * np.pi * 2.5 * t))

save()
