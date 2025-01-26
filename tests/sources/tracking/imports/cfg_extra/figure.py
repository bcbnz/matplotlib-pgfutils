# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from pgfutils import save, setup_figure

setup_figure(height=0.3)

from custom_lib import get_data
from matplotlib import pyplot as plt

t, s = get_data()
plt.plot(t, s)

save()
