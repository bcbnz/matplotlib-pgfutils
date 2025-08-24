# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

from pgfutils import save, setup_figure, tracker

setup_figure(width=1, height=1)

import base64
import os

from matplotlib import pyplot as plt
import numpy as np

t = np.linspace(0, 10, 201)
s = np.sin(2 * np.pi * 0.5 * t)

# This is only for testing purposes.
# You shouldn't need to do this in a normal script!
os.fdopen = tracker.wrap_file_opener(os.fdopen)

fd = os.open("test_fdopen.png", os.O_WRONLY | os.O_CREAT)
with os.fdopen(fd, "wb") as f:
    img = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFhAJ/wlse"
        "KgAAAABJRU5ErkJggg=="
    )
    f.write(base64.b64decode(img))

plt.plot(t, s)
save()
