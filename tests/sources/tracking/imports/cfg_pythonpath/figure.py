from pgfutils import setup_figure, save
setup_figure(height=0.3)

from custom_lib import get_data
from matplotlib import pyplot as plt

t, s = get_data()
plt.plot(t, s)

save()
