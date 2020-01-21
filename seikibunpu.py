import numpy as np
from scipy.stats import norm
import sys


# p = norm.cdf(x=x, loc=mu, scale=sigma)
# print(p)

# for E_bN_0 in [1.0, 1.5, 2.0, 2.5, 3.0]:
#     bunsan = 10**(-E_bN_0/10)
#     print(bunsan)

for sigma in [0.794328, 0.707946, 0.630957, 0.562341, 0.501187]:
    P = norm.cdf(x=0, loc=1, scale = sigma)
    print(P)