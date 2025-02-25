# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from pgfutils import save, setup_figure

setup_figure(width=1, height=0.4, extra_tracking="netCDF4")

import matplotlib.pyplot as plt
import netCDF4
import numpy as np

t = np.linspace(0, 1, 101)
s = np.sin(2 * np.pi * 3 * t)

ds = netCDF4.Dataset("test_output.nc", "w")
samples = ds.createDimension("sample", len(t))
times = ds.createVariable("time", "f8", ("sample",))
times[:] = t
voltage = ds.createVariable("voltage", "f8", ("sample",))
voltage[:] = s
ds.close()

plt.plot(t, s)

save()
