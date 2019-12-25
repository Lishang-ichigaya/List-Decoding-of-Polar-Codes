import numpy as np
from decimal import Decimal
from decimal import getcontext
from numpy.random import rand
getcontext().prec = 50
from Encoder import GetPermutationMatrix

F=np.array([[1,0],[1,1]], dtype=np.uint8)
two = 2

A = np.kron(np.identity(2, dtype=np.uint8), F)
B = GetPermutationMatrix(2)
C = np.kron(np.identity(two, dtype=np.uint8), F)

G_4 = np.dot(np.dot(A, B), C)

A = np.kron(np.identity(4, dtype=np.uint8), F)
B = GetPermutationMatrix(3)
C = np.kron(np.identity(two, dtype=np.uint8), G_4)

G_8 = np.dot(np.dot(A, B), C)

u = np.array([0,0,0,1,0,1,1,1])
print(np.dot(u, G_8)%2)