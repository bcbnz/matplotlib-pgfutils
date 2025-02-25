# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from pgfutils import save, setup_figure

setup_figure(width=1, height=1)

from matplotlib import pyplot as plt
from matplotlib.lines import Line2D

cmap = plt.cm.coolwarm
custom_lines = [
    Line2D([0], [0], color=cmap(0), lw=4),
    Line2D([0], [0], color=cmap(0.5), lw=4),
    Line2D([0], [0], color=cmap(1), lw=4),
]

fig = plt.figure(frameon=False)
ax = fig.add_axes([0, 0, 1, 1])
ax.axis("off")
plt.legend(custom_lines, ("One", "Two", "Three"), loc="center")

save()
