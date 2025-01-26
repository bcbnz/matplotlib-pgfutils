# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from pgfutils import save, setup_figure


setup_figure(width=0.95, height=0.4)

from matplotlib import pyplot as plt
import numpy as np


noise = np.random.randn(512, 256) + 1j * np.random.randn(512, 256)
plt.imshow(np.abs(noise) ** 2, interpolation="nearest", aspect="auto")
plt.colorbar()

save()
