import numpy as np
from numpy.random import rand
from numpy.random import normal
import time
from message import Message


class BSC:
    def __init__(self, P):
        self.P = P
        self.input = np.array([], dtype=np.uint8)
        self.output = np.array([], dtype=np.uint8)

    def Transmission(self):
        n = np.size(self.input)
        noise = rand(n)
        binnoise = np.zeros([n], dtype=np.uint8)
        binnoise[np.where(self.P > noise)] = 1
        self.output = (self.input + binnoise) % 2


class BEC:
    def __init__(self, e):
        self.e = e
        self.input = np.array([], dtype=np.uint8)
        self.output = np.array([], dtype=np.uint8)
    
    def Transmission(self):
        n = np.size(self.input)
        noise = rand(n)
        output = self.input
        output[np.where(self.e > noise)] = 3
        self.output = output

class AWGN:
    def __init__(self, snr, R):
        self.variance = 10**(-snr/10)/(2*R)
        self.input = np.array([], dtype=np.uint8)
        self.output = np.array([], dtype=np.uint8)
    
    def Transmission(self):
        n = np.size(self.input)
        chanel_input = np.array([+1.0 if n_i == 0 else -1.0 for n_i in self.input])
        gauss_nose = normal(0, np.sqrt(self.variance), n)
        chanel_output = chanel_input + gauss_nose
        self.output = chanel_output
        return chanel_output




if __name__ == "__main__":
    N = 256
    kaisu = 1000
    sum0 = 0
    P = 0.1

    for i in range(kaisu):
        input = np.random.randint(0,2,N) 
        # input = np.full([N], 1, dtype=np.uint8)

        bsc = BSC(P)
        bsc.input = input
        bsc.Transmission()

        output = bsc.output
        hikaku = input^output
        sum0 += len(np.where(hikaku ==1)[0])
        # print(len(np.where(output ==3)[0]))
        # print(sum)
        # print(hikaku)
    print("誤り率", sum0 / (N * kaisu))
