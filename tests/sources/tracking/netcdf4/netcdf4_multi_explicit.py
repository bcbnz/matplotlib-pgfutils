from pgfutils import save, setup_figure


setup_figure(width=1, height=0.4)

import matplotlib.pyplot as plt
import netCDF4


ds = netCDF4.MFDataset(["mftest0.nc", "mftest1.nc", "mftest2.nc"])
plt.plot(ds["x"][:])

save()
