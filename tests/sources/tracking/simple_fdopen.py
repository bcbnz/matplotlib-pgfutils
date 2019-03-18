from pgfutils import setup_figure, save, _file_tracker
setup_figure(width=1, height=1)

import numpy as np
from matplotlib import pyplot as plt
import base64
import os

t = np.linspace(0, 10, 201)
s = np.sin(2 * np.pi * 0.5 * t)

# This is only for testing purposes.
# You shouldn't need to do this in a normal script!
os.fdopen = _file_tracker(os.fdopen)

fd = os.open("test_fdopen.png", os.O_WRONLY | os.O_CREAT)
with os.fdopen(fd, 'wb') as f:
    img = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFhAJ/wlseKgAAAABJRU5ErkJggg=="
    f.write(base64.b64decode(img))

plt.plot(t, s)
save()
