import numpy as np
from decimal import Decimal
from decimal import getcontext
getcontext().prec = 128

a = Decimal("0.55")
b = Decimal("0.11")

print(a/b)