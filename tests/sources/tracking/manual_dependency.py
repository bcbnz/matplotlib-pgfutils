from pgfutils import setup_figure, add_dependencies, save
setup_figure(width=1, height=1)

import numpy as np
from matplotlib import pyplot as plt

t = np.linspace(0, 10, 201)
s = np.sin(2 * np.pi * 0.5 * t)

add_dependencies("data.file")

plt.plot(t, s)
save()
