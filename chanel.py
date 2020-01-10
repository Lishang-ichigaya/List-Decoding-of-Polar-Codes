import numpy as np
from numpy.random import rand
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
        for i in range(np.size(self.input)):
            tmp = self.input[i] if rand() > self.e else 3
            self.output = np.insert(self.output, i, tmp)


if __name__ == "__main__":
    #    N = 16
    #    input = np.array([1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0])
    #    bsc = BSC(1)
    #    bsc.input = input
    #    bsc.Transmission2()
    #    output = bsc.output
    #    print(input)
    #    print(output)

    N = 512
    kaisu = 10000
    sum = 0
    P = 0.7
    a = 0
    # start = time.time()
    # for i in range(kaisu):
    #     input = np.full([N], a, dtype=np.uint8)

    #     bsc = BSC(P)
    #     bsc.input = input
    #     bsc.Transmission()

    #     output = bsc.output
    #     sum += np.count_nonzero(output)
    #     #print(sum)
    #     #print(output)
    # end = time.time()
    # print("高速化なし")
    # print("時間", end-start)
    # print("誤り率", sum / (N * kaisu))

    sum = 0
    start = time.time()
    for i in range(kaisu):
        input = np.full([N], a, dtype=np.uint8)

        bsc = BSC(P)
        bsc.input = input
        bsc.Transmission()

        output = bsc.output
        sum += np.count_nonzero(output)
        # print(sum)
        # print(output)
    end = time.time()
    print("高速化あり")
    print("時間", end-start)
    print("誤り率", sum / (N * kaisu))
