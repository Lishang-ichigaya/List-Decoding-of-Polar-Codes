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
    p = Pool(8)
    result = p.imap_unordered(pa, range(4))

    for _ in result:
        pass

    p.close
    