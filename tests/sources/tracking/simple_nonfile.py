# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from pgfutils import _file_tracker, save, setup_figure


setup_figure(width=1, height=1)

import base64
import os

from matplotlib import pyplot as plt
import numpy as np


t = np.linspace(0, 10, 201)
s = np.sin(2 * np.pi * 0.5 * t)

# This is only for testing purposes.
# You shouldn't need to do this in a normal script!
os.open = _file_tracker(os.open)

fd = os.open("test_nonfile.png", os.O_WRONLY | os.O_CREAT)
img = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFhAJ/wlseKg"
    "AAAABJRU5ErkJggg=="
)
os.write(fd, base64.b64decode(img))
os.close(fd)

plt.plot(t, s)
save()
