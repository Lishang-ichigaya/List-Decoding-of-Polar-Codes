import numpy as np
from BMSchannel import BMSchannel
from degrading import degrading_merge

def getSymmetricChannelCapacity(channel):
    if type(channel) != BMSchannel:
        raise TypeError("Use BMSchannel")
    I = 0
    for x in [0, 1]:
        for y in range(channel.N):
            I += channel.W[x][y] * np.log2(channel.W[x][y]/(channel.W[0][y]+channel.W[1][y]))
    I = 1+0.5*I
    return I


if __name__ == "__main__":
    N = 1024
    M = int(np.log2(N))
    mu = 8
    W_0 = [[0.89, 0.11],[0.11, 0.89]]
    

    for i in range(N):
        b = bin(i)[2:]
        b = b.zfill(M)
        Q = BMSchannel(W_0, 2)

        for j in range(M):
            if b[j] == '0':
                W = BMSchannel.mul_sq(Q)
            else:
                W = BMSchannel.mul_cir(Q)
            deg = degrading_merge(W, mu)
            Q = deg.merge()
        
        I = getSymmetricChannelCapacity(Q)
        print(I)

