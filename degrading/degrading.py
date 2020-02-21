import numpy as np
from CaliculateW import CalculateW_BSC_2
from BMSchannel import BMSchannel
import time
import copy


class _deg_data():
    def __init__(self, a_0, b_0, a_1, b_1):
        self.a_0 = a_0
        self.b_0 = b_0
        self.a_1 = a_1
        self.b_1 = b_1
        self.deltaI = self._calDeltaI(a_0, b_0, a_1, b_1)

    def _calDeltaI(self, a_0, b_0, a_1, b_1):
        def C(a, b): return -(a+b)*np.log2((a+b)/2) \
            + a*np.log2(a) \
            + b*np.log2(b)
        C_a0b0 = C(a_0, b_0)
        C_a1b1 = C(a_1, b_1)
        C_apbp = C(a_0+a_1, b_0+b_1)
        return C_a0b0 + C_a1b1 - C_apbp


class degrading_merge():
    def __init__(self, channel, mu):
        """
        degrading_mergeに関するクラス\n
        W:元の通信路に関するBMSchannelクラス, mu:degradingした通信路の最大出力数 
        """
        self.channel = channel
        self.mu = mu
        self.data_list = []
        if type(channel) is not BMSchannel:
            raise TypeError("BMSchannelクラスを使用してね")
        data = []
        for i in range(channel.N//2-1):
            d = _deg_data(channel.W[0][i], channel.W[1][i], channel.W[0][i+1], channel.W[1][i+1])
            data.append(d)
        # print(len(data))
        self.data_list = data

    def _getMin(self):
        deltaI_list = [self.data_list[i].deltaI for i in range(len(self.data_list))]
        m = min(deltaI_list)
        i = deltaI_list.index(m)
        return i


    def _ConstructQ(self):
        Q_0 = [self.data_list[0].a_0]
        Q_1 = [self.data_list[0].b_0]
        for i in range(len(self.data_list)):
            Q_0.append(self.data_list[i].a_1)
            Q_1.append(self.data_list[i].b_1)
        tmp = copy.copy(Q_0)
        Q_0.extend(Q_1)
        Q_1.extend(tmp)

        Q = BMSchannel([Q_0, Q_1], len(Q_0))
        tmp = Q.W.T
        tmp = np.array(sorted(tmp, key=lambda x: x[0]/x[1]))
        Q.W = tmp.T
        return Q

    def merge(self):
        l = self.channel.N//2
        nu = self.mu//2
        while l > nu:
            min_index = self._getMin()
            d = self.data_list[min_index]
            a_p = d.a_0 + d.a_1
            b_p = d.b_0 + d.b_1
            if min_index - 1 >= 0:
                dLeft = self.data_list[min_index - 1]
            else:
                dLeft = None
            if min_index + 1 < len(self.data_list):
                dRight = self.data_list[min_index + 1]
            else:
                dRight = None
            if dLeft != None:
                a_0 = dLeft.a_0
                b_0 = dLeft.b_0
                a_1 = a_p
                b_1 = b_p
                d = _deg_data(a_0, b_0, a_1, b_1)
                self.data_list[min_index - 1] = d
            if dRight != None:
                a_0 = a_p
                b_0 = b_p
                a_1 = dRight.a_1
                b_1 = dRight.b_1
                d = _deg_data(a_0, b_0, a_1, b_1)
                self.data_list[min_index + 1] = d
            self.data_list.pop(min_index)
            l = l - 1

        Q = self._ConstructQ()
        return Q


if __name__ == "__main__":
    W = [[0.89, 0.11], [0.11, 0.89]]
    W_0 = BMSchannel(W, 2)

    W_1 = [None]*2
    W_2 = [None]*4
    W_3 = [None]*8
    for m in range(3):
        for i in range(2//2):
            W_1[i] = BMSchannel.mul_sq(W_0)
            W_1[i+1] = BMSchannel.mul_cir(W_0)
        for i in range(4//2):
            W_2[2*i] = BMSchannel.mul_sq(W_1[i])
            W_2[2*i+1] = BMSchannel.mul_cir(W_1[i])
        for i in range(8//2):
            W_3[2*i] = BMSchannel.mul_sq(W_2[i])
            W_3[2*i+1] = BMSchannel.mul_cir(W_2[i])

    Qtrue = W_3[5]
    merge = degrading_merge(Qtrue, 8)
    Q = merge.merge()

    
    I = 0
    for x in [0, 1]:
        for y in range(Qtrue.N):
            I += Qtrue.W[x][y] * np.log2(Qtrue.W[x][y]/(Qtrue.W[0][y]+Qtrue.W[1][y]))
    I = 1+0.5*I
    print(I)

    I = 0
    for x in [0, 1]:
        for y in range(Q.N):
            I += Q.W[x][y] * np.log2(Q.W[x][y]/(Q.W[0][y]+Q.W[1][y]))
    I = 1+0.5*I
    print(I)

    print(Qtrue.N,"\n",Qtrue.W)
    # for y in range(Qtrue.N):
    #     print(Qtrue.W[0][y]/Qtrue.W[1][y])
    
    print("-----------------")
    print(Q.N,"\n",Q.W)
    # print(Q.N == len(Q.W[0]))

    # for y in range(Q.N):
    #     print(Q.W[0][y]/Q.W[1][y])
