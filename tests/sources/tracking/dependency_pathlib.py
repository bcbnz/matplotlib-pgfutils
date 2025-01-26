# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from pgfutils import save, setup_figure

setup_figure(width=1, height=1)

import pathlib

from matplotlib import pyplot as plt
import numpy as np

datastr = pathlib.Path("scatter.csv").read_text()
data = np.genfromtxt(datastr.splitlines(), delimiter=",", dtype=int)

x = data[:, :3]
y = data[:, 3:]

plt.scatter(x, y)

save()
