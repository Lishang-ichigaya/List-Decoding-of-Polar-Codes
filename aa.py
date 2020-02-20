import time
import numpy as np

if __name__ == "__main__":
    a = 0b1001

    for i in range(4):
        print(a%(2**i))
