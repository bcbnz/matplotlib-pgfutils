# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from pgfutils import save, setup_figure

setup_figure(width=1, height=1)

from matplotlib import pyplot as plt
import numpy as np

rng = np.random.default_rng(seed=4242)
d = rng.random((128, 128))
plt.imshow(d)

save()
