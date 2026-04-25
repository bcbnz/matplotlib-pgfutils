# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from pgfutils import save, setup_figure

setup_figure(width=1, height=1, separate_legend=True)

from matplotlib import pyplot as plt
import numpy as np

t = np.arange(0, 1, 0.005)
s1 = np.sin(2 * np.pi * t)
s2 = np.sin(4 * np.pi * t)
s3 = np.sin(6 * np.pi * t)

# Disable all other frames and sources of text.
fig = plt.figure(frameon=False)
ax = fig.add_axes([0, 0, 1, 1])
ax.axis("off")

ax.plot(t, s1, label="One")
ax.plot(t, s2, label="Two")
ax.plot(t, s3, label="Three")
ax.legend()

save()
