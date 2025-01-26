# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from pgfutils import save, setup_figure


setup_figure(width=1, height=1)

from matplotlib import pyplot as plt
import numpy as np


data = np.load("noise.npy")

x = data[:, :3]
y = data[:, 3:6]

plt.scatter(x, y)

save()
