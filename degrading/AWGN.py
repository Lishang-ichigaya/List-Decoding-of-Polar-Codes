import numpy as np
from scipy.stats import norm
from scipy import integrate
import matplotlib as plt

from BMSchannel import BMSchannel
from  degrading import degrading_merge_AWGN

def func(x):
    stdev = np.sqrt(0.63095)
    f0 = norm.pdf(x=x, loc=+1, scale=stdev)
    f1 = norm.pdf(x=x, loc=-1, scale=stdev)

    func = (f0 + f1) - f0*np.log2((f0 + f1)/f0) - f1*np.log2((f0 + f1)/f1)
    return func

if __name__ == "__main__":
    def getSymmetricChannelCapacity(channel):
        if type(channel) != BMSchannel:
            raise TypeError("Use BMSchannel")
        I = 0
        for x in [0, 1]:
            for y in range(channel.N):
                I += channel.W[x][y] * np.log2(channel.W[x][y]/(channel.W[0][y]+channel.W[1][y]))
        I = 1+0.5*I
        return I
    N = 10**(-2/10)

    C_0 = integrate.quad(func, 0, 5)[0]
    C_1 = 0.5*np.log2(1+ 1/N)
    a = degrading_merge_AWGN(2, 0.5, 1024)
    Q = a.merge()
    C_2 = getSymmetricChannelCapacity(Q)

    print(C_0)
    print(C_1)
    print(C_2)