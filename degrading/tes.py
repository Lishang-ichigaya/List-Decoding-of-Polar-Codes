import numpy as np

if __name__ == "__main__":
    a = [0,1,2,3,4,5,6,7,8,9,10]

    b = sorted(a, key=lambda x: x%5)
    print(b)