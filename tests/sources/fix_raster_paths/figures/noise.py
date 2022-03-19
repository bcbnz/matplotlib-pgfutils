from pgfutils import save, setup_figure


setup_figure(width=0.95, height=0.4)

from matplotlib import pyplot as plt
import numpy as np


noise = np.random.randn(512, 256)
plt.imshow(noise, interpolation="nearest", aspect="auto")
plt.colorbar()

save()
