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
    p = 0.03
    W_0 = [[1-p, p],[p, 1-p]]
    I_W = [None]*N
    filename = "sort_I_"+str(M)+"_"+str(p)+".dat"
    

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
        I_W[i] = I
        # print(i)
    sorted_index = np.argsort(I_W)
    print(sorted_index)
    with open(filename, mode='a', encoding='utf-8') as f:
        for i in range(N):
            f.write(str(sorted_index[i])+" ")

    

