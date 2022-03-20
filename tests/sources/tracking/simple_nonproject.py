from pgfutils import save, setup_figure


setup_figure(width=1, height=1)

import base64
from pathlib import Path
import tempfile

from matplotlib import pyplot as plt
import numpy as np


t = np.linspace(0, 10, 201)
s = np.sin(2 * np.pi * 0.5 * t)

with open(Path(tempfile.gettempdir()) / "test_nonproject.png", "wb") as f:
    img = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFhAJ/wlse"
        "KgAAAABJRU5ErkJggg=="
    )
    f.write(base64.b64decode(img))

plt.plot(t, s)
save()
