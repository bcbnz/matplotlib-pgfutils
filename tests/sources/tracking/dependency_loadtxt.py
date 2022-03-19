from pgfutils import save, setup_figure


setup_figure(width=1, height=1)

from matplotlib import pyplot as plt
import numpy as np


data = np.loadtxt("scatter.csv", delimiter=",", dtype=int)

x = data[:, :3]
y = data[:, 3:]

plt.scatter(x, y)

save()
