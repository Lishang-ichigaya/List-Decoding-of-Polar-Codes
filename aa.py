import time
import numpy as np

if __name__ == "__main__":
    t0 = time.time()
    a = np.array([], dtype=np.uint8)
    b = np.array([], dtype=np.uint8)
    for i in range(2048):
        a = np.insert(a,i,np.array([0]))
    t1 = time.time()
    for i in range(2048):
        b = np.insert(b,i,0)
    t2 = time.time()
    print(a)
    print(b)
    print(t1-t0, t2-t1)