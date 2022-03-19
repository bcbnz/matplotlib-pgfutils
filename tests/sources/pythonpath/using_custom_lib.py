from pgfutils import save, setup_figure


setup_figure(width=1, height=1)

from custom_library import get_data
import matplotlib.pyplot as plt


t, s = get_data()
plt.plot(t, s)

save()
