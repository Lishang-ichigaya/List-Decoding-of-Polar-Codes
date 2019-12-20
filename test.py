import numpy as np

L = 8

a = np.array([0.1, 0.8, 0.2, 0.6, 0.1, 0.4, 0.9])
b = np.argsort(a)
c = b[-1::-1]

print(a)
print(b)
print(c[:2])

