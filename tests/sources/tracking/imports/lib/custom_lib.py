import numpy as np

def get_data():
    t = np.linspace(0, 1, 100)
    s = np.sin(2 * np.pi * 4 * t)
    return t, s
