from pgfutils import setup_figure, save
setup_figure(width=1, height=1)

import numpy as np
from matplotlib import pyplot as plt
import pathlib

datastr = pathlib.Path("scatter.csv").read_text()
data = np.genfromtxt(datastr.splitlines(), delimiter=',', dtype=int)

x = data[:, :3]
y = data[:, 3:]

plt.scatter(x, y)

save()
