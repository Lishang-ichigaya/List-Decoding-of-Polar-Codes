import time
import sys
from multiprocessing import Pool

def pa(i):
    for i in range(1, 101):
        time.sleep(0.1)
        # sys.stdout.write("\r")
        sys.stdout.write("{0}%".format(i))
        sys.stdout.flush()
    sys.stdout.write("\n")

if __name__ == "__main__":
    a = [1, 2, 3, 5, 7, 11, 13, 17]
    b = [x-1 for x in a]
    print(b)