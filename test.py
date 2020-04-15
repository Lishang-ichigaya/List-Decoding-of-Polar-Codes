import numpy as np

if __name__ == "__main__":
    a = [[0, "j"], [5,"d"], [7, "a"]]
    b = sorted(a, key= lambda x: x[1], reverse=True)
    print(b)



