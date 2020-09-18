import time
import sys
from multiprocessing import Pool
import numpy as np

# def pa(i):
#     for i in range(1, 101):
#         time.sleep(0.1)
#         # sys.stdout.write("\r")
#         sys.stdout.write("{0}%".format(i))
#         sys.stdout.flush()
#     sys.stdout.write("\n")

if __name__ == "__main__":
    L = [np.array([], dtype=np.uint8) for _ in range(5)]
    print(L)