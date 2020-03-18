import numpy as np
from BMSchannel import BMSchannel
import degrading
from multiprocessing import Pool
import notification
import copy

N = 256
M = int(np.log2(N))
mu = 32
parallelnum = 48

# p = 0.03
# W_0 = [[1-p, p],[p, 1-p]]
# filename = "sort_I_"+str(M)+"_"+str(p)+".dat"
snr = 1
R = 1/2
filename = "sort_I_AWGN_"+str(M)+"_"+str(R)+"_"+str(snr)+"_"+".dat"

awgn_deg = degrading.degrading_merge_AWGN(snr, R, 128)
Q_AWGN = awgn_deg.merge()

def getSymmetricChannelCapacity(channel):
    if type(channel) != BMSchannel:
        raise TypeError("Use BMSchannel")
    I = 0
    for x in [0, 1]:
        for y in range(channel.N):
            I += channel.W[x][y] * np.log2(channel.W[x][y]/(channel.W[0][y]+channel.W[1][y]))
    I = 1+0.5*I
    return I

def getDegradingChannelCapacity(i):
        b = bin(i)[2:]
        b = b.zfill(M)
        # Q = BMSchannel(W_0, 2)
        Q = copy.deepcopy(Q_AWGN)

        for j in range(M):
            if b[j] == '0':
                W = BMSchannel.mul_sq(Q)
            else:
                W = BMSchannel.mul_cir(Q)
            deg = degrading.degrading_merge(W, mu)
            Q = deg.merge()
        
        I = getSymmetricChannelCapacity(Q)
        return I

if __name__ == "__main__":
    p = Pool(parallelnum)
    I_W = []
    I_W_iterator = p.imap(getDegradingChannelCapacity, range(N))
    for I in I_W_iterator:
        print(I)
        I_W.append(I)
    p.close()
    # for i in range(N):
    #     I = getDegradingChannelCapacity(i)
    #     I_W[i] = I
    #     print(i)
    
    sorted_index = np.argsort(I_W)
    print(sorted_index)
    with open(filename, mode='a', encoding='utf-8') as f:
        for i in range(N):
            f.write(str(sorted_index[i])+" ")

    try:
        notification.Notice()
    except Exception as e:
        print(e)

    

