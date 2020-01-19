import numpy as np
import time
from multiprocessing import Pool

def Longtime(i):
    time.sleep(1)
    print(i)

def Fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return Fib(n-1) + Fib(n-2)

if __name__ == "__main__":
    p = Pool(4)
    st = time.time()
    res = p.map(Fib, range(35))
    ed = time.time()
    for i in res:
        print(str(i)+", ")
    # st = time.time()
    # for i in range(35):
    #     Fib(i)
    # ed = time.time()
    print(ed-st)


