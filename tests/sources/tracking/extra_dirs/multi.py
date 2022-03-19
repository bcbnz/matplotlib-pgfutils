from pgfutils import add_dependencies, save, setup_figure


setup_figure(width=1, height=1)

from matplotlib import pyplot as plt
import numpy as np


noise = np.load("../noise.npy")
plt.imshow(noise)
plt.colorbar()

data = np.loadtxt("scatter.csv", delimiter=",", dtype=int)

x = data[:, :3]
y = data[:, 3:]

plt.scatter(x, y)

add_dependencies("../../extra.file")
save()
