from pgfutils import setup_figure, save
setup_figure(width=1, height=1)

import matplotlib.pyplot as plt
from custom_library import get_data

t, s = get_data()
plt.plot(t, s)

save()
