# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from pgfutils import save, setup_figure

setup_figure(width=1, height=0.4)

import matplotlib.pyplot as plt
import netCDF4

ds = netCDF4.Dataset("sine.nc")
plt.plot(ds["time"][:], ds["voltage"][:])

save()
