import numpy as np
from decimal import Decimal
from decimal import getcontext
getcontext().prec = 50

a = Decimal("1")

for i in range(100):
    a /= 11
    print(a)