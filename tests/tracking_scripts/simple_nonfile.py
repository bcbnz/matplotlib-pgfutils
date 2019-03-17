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
os.open = _file_tracker(os.open)

fd = os.open("test_nonfile.png", os.O_WRONLY | os.O_CREAT)
img = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFhAJ/wlseKgAAAABJRU5ErkJggg=="
os.write(fd, base64.b64decode(img))
os.close(fd)

plt.plot(t, s)
save()
