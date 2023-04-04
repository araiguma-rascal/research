import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class CONST:
    def __init__(self):
        self.BOHR_MAG = 9.2740100783e-24
        self.DIRAC_CONST = 6.62607004E-34 / (2*np.pi)
        self.G_FACTOR = 1.95
        self.GYROMAG_RATIO = self.G_FACTOR * self.BOHR_MAG / self.DIRAC_CONST
        self.H_0 = 0.746704067  # mT
        self.ALPHA_LSMO = 0.00157
