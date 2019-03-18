from pgfutils import setup_figure, save
setup_figure(width=1, height=1)

import numpy as np
from matplotlib import pyplot as plt
import os.path

data = np.load('noise.npy')

x = data[:, :3]
y = data[:, 3:6]

plt.scatter(x, y)

save()
