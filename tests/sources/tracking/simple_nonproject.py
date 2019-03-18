from pgfutils import setup_figure, save
setup_figure(width=1, height=1)

import numpy as np
from matplotlib import pyplot as plt
import base64
import os.path
import tempfile

t = np.linspace(0, 10, 201)
s = np.sin(2 * np.pi * 0.5 * t)

with open(os.path.join(tempfile.gettempdir(), "test_nonproject.png"), 'wb') as f:
    img = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFhAJ/wlseKgAAAABJRU5ErkJggg=="
    f.write(base64.b64decode(img))

plt.plot(t, s)
save()
