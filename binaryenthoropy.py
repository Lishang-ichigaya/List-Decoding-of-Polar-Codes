import numpy as np
import sys

def BinaryEntropy(p):
    return -p*np.log2(p)-(1-p)*np.log2(1-p)

if __name__ == "__main__":
    p = float(sys.argv[1])
    hp = BinaryEntropy(p)
    print(hp)