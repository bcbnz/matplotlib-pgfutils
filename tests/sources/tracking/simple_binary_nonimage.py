# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from pgfutils import save, setup_figure


setup_figure(width=1, height=1)

from matplotlib import pyplot as plt
import numpy as np


t = np.linspace(0, 10, 201)
s = np.sin(2 * np.pi * 0.5 * t)

data = np.random.randn(100, 100)

with open("test.npy", "wb") as f:
    np.save(f, data)

plt.plot(t, s)
save()
