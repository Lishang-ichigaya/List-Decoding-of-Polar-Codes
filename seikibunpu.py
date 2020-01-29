import numpy as np
from scipy.stats import norm
import sys


# p = norm.cdf(x=x, loc=mu, scale=sigma)
# print(p)

# for E_bN_0 in [1.0, 1.5, 2.0, 2.5, 3.0]:
#     bunsan = 10**(-E_bN_0/10)
#     print(bunsan)
if __name__ == "__main__":
    sigma = 0.50
    F__puls1 = norm.cdf(x=0, loc=1, scale = sigma)
    F_minus1 = norm.cdf(x=0, loc=-1, scale = sigma)
    P = (F__puls1)/(F__puls1 + F_minus1)

    print(P)