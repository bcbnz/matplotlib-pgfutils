from pgfutils import setup_figure, save, _config
setup_figure(width=0.5, height=0.4, preamble_substitute=True,
    preamble="\\usepackage{fontspec}\n\\setmainfont{CothamSans}[Path=${basedir}/../Cotham/,Extension=.otf]"
)

from matplotlib import pyplot as plt
import numpy as np
from scipy.special import j1

x = np.linspace(-4, 4, 201)
plt.plot(x, j1(x))

save()
