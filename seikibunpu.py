import numpy as np
from scipy.stats import norm

sigma = 0.794
s=3.0
p = norm.cdf(x=0, loc=s, scale=sigma)
print(p)