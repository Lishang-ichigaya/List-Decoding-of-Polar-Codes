import numpy as np

if __name__ == "__main__":
    a = np.array([1,2,3,4,5,6,7,8,9,10], dtype=np.uint8)
    b = np.array([0,4,7])

    a[1:] =4
    print(a)