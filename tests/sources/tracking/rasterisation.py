from pgfutils import setup_figure, save
setup_figure(width=1, height=1)

import numpy as np
from matplotlib import pyplot as plt

d = np.random.randn(128,128)
plt.imshow(d)

save()
