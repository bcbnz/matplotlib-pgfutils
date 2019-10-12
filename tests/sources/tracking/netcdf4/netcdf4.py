from pgfutils import setup_figure, save
setup_figure(width=1, height=0.4)

import netCDF4
import matplotlib.pyplot as plt

ds = netCDF4.Dataset("sine.nc")
plt.plot(ds['time'], ds['voltage'])

save()
