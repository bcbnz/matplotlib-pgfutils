import numpy as np

def get_data():
    t = np.linspace(0, 3, 200)
    s = np.sin(2 * np.pi * 3 * t)
    return t, s
