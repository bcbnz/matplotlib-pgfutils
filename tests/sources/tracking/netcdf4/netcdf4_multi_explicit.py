from pgfutils import setup_figure, save
setup_figure(width=1, height=0.4)

import netCDF4
import matplotlib.pyplot as plt

ds = netCDF4.MFDataset(["mftest0.nc", "mftest1.nc", "mftest2.nc"])
plt.plot(ds["x"][:])

save()
