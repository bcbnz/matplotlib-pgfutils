from pgfutils import setup_figure, save, _config
setup_figure(width=0.95, height=0.4)

from matplotlib import pyplot as plt
import numpy as np

t = np.linspace(-4, 4, 201)
plt.plot(t, 2 * np.sin(2 * np.pi * 2.5 * t))

save()
