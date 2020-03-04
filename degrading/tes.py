import numpy as np
from scipy.stats import norm

def BinaryEntropy(p):
    return -p*np.log2(p)-(1-p)*np.log2(1-p)

if __name__ == "__main__":
    N = 10**(-2/10)
    a = 1 - norm.cdf(np.sqrt(1/N), 0, 1)
    
    C = 1 - BinaryEntropy(a)
    print(C)