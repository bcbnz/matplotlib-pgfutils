# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from pgfutils import save, setup_figure

setup_figure(width=0.95, height=0.4)

from matplotlib import pyplot as plt
import numpy as np

rng = np.random.default_rng(seed=100)
noise = rng.random((512, 256))
plt.imshow(noise, interpolation="nearest", aspect="auto")
plt.colorbar()

save()
