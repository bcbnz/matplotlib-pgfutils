from pgfutils import setup_figure, save
setup_figure(width=0.95, height=0.4)

import numpy as np
from matplotlib import pyplot as plt

noise = np.random.randn(512, 256) + 1j*np.random.randn(512, 256)
plt.imshow(np.abs(noise)**2, interpolation='nearest', aspect='auto')
plt.colorbar()

save()
