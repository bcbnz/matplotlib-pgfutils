from pgfutils import save, setup_figure


setup_figure(width=1, height=0.4)

import matplotlib.pyplot as plt
import netCDF4


ds = netCDF4.Dataset("sine.nc")
plt.plot(ds["time"], ds["voltage"])

save()
