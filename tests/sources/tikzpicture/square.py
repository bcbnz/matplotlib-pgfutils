# SPDX-FileCopyrightText: Blair Bonnett
# SPDX-License-Identifier: BSD-3-Clause

# Set up the figure environment.
from pgfutils import save, setup_figure


setup_figure(width=0.9, height=0.4)

from matplotlib import pyplot as plt
import numpy as np


# Generate square wave from a few terms of its Fourier series.
f = 3
t = np.linspace(0, 1, 501)
square = np.zeros(t.shape)
for n in range(1, 12, 2):
    # Create this harmonic and plot it as a dashed
    # partially-transparent line.
    component = np.sin(2 * n * np.pi * f * t) / n
    plt.plot(t, component, "--", alpha=0.4)

    # Add it to the overall signal.
    square += component

# Scale the final sum.
square *= 4 / np.pi

# Plot and label the figure.
plt.plot(t, square, "C0")
plt.xlim(0, 1)
plt.ylim(-1.2, 1.2)
plt.xlabel("Time (s)")
plt.ylabel("Amplitude (V)")

# Save as a PGF image.
save()
