import numpy as np

if __name__ == "__main__":
    a = [[2, 3],[1, 5],[14, 21], [87, 2]]
    b = sorted(a, key=lambda x: x[0], reverse=True)
    print(a)
    print(b)