from pgfutils import save, setup_figure


setup_figure(width=1, height=1)

from matplotlib import pyplot as plt
import numpy as np


d = np.random.randn(128, 128)
plt.imshow(d)

save()
