# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from pgfutils import add_dependencies, save, setup_figure

setup_figure(width=1, height=1)

from matplotlib import pyplot as plt
import numpy as np

t = np.linspace(0, 10, 201)
s = np.sin(2 * np.pi * 0.5 * t)

add_dependencies("data.file")

plt.plot(t, s)
save()
