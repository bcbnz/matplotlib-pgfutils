from pgfutils import setup_figure, save
setup_figure(width=1, height=1)

import numpy as np
from matplotlib import pyplot as plt
import os.path

noise = np.load('tests/tracking_scripts/noise.npy')
plt.imshow(noise)
plt.colorbar()

data = np.loadtxt('tests/tracking_scripts/scatter.csv', delimiter=',', dtype=np.int)

x = data[:, :3]
y = data[:, 3:]

plt.scatter(x, y)

save()
