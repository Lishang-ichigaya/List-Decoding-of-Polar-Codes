import numpy as np
from decimal import Decimal
from numpy.random import rand

a = Decimal(rand())
b = Decimal(rand())

for i in range(10000):
    a *= 10*Decimal(rand())
    b *= 110000*Decimal(rand())

print(a)
print(b)
print(a*b)
print(a/b)

