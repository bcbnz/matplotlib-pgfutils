# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from pgfutils import save, setup_figure

setup_figure(width=0.95, height=0.4)

from matplotlib import pyplot as plt
import numpy as np

rng = np.random.default_rng(seed=1010)
noise = rng.standard_normal((512, 256)) + 1j * rng.standard_normal((512, 256))
plt.imshow(np.abs(noise) ** 2, interpolation="nearest", aspect="auto")
plt.colorbar()

save()
