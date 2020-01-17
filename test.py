import numpy as np
from scipy.stats import norm

if __name__ == "__main__":
    a = norm.cdf(x=0, loc=1, scale=0.645)
    print(a)