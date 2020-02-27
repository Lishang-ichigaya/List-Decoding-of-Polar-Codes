import numpy as np
from scipy.stats import norm
import matplotlib as plt

if __name__ == "__main__":
    y = 0.4
    stdev = 1

    MU_0 = -1
    MU_1 = -MU_0

    y_0 = norm.pdf(x=y, loc=MU_0, scale=stdev)
    y_1 = norm.pdf(x=y, loc=MU_1, scale=stdev)
    print(y_0/y_1-np.exp(-2*y/(stdev*stdev)))