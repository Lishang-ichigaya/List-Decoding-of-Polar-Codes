import numpy as np
from scipy.stats import norm
from BMSchannel import BMSchannel
import time
import copy

import matplotlib.pyplot as plt


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


class degrading_merge_AWGN():
    def __init__(self, snr, R, mu):
        """
        AWGN通信路のdegrading_mergeに関するクラス\n
        snr: AWGN通信路のSN比(E_b/N_0[db])\n
        R:   符号化レート(k/n)\n
        mu: degradingした通信路の最大出力数 
        """
        self.mu = mu
        self.variance = 10**(-snr/10)/(2*R)

    def merge(self):
        """
        AWGN通信路のdegrading_mergeを行うメソッド
        戻り地: degrading mergeで得られるBMSchanelクラス
        """
        A_i = self._GetSubset()
        # print(A_i)

        Q_0 = []
        Q_1 = []
        for i in range(self.mu//2):
            y_left = A_i[i][0]
            y_right = A_i[i][1]
            stdev = np.sqrt(self.variance)
            
            right_cdf_0 = norm.cdf(x=y_right, loc=+1, scale=stdev)
            left_cdf_0 = norm.cdf(x=y_left, loc=+1, scale=stdev)
            q_0 = right_cdf_0 - left_cdf_0
            
            right_cdf_1 = norm.cdf(x=y_right, loc=-1, scale=stdev)
            left_cdf_1 = norm.cdf(x=y_left, loc=-1, scale=stdev)
            q_1 = right_cdf_1 - left_cdf_1
            if q_0<0 or q_1<0:
                print(i)

            Q_0.append(q_0)
            Q_1.append(q_1)
        
        tmp = copy.copy(Q_0)
        Q_0.extend(Q_1)
        Q_1.extend(tmp)

        Q = BMSchannel([Q_0, Q_1], len(Q_0))
        tmp = Q.W.T
        tmp = np.array(sorted(tmp, key=lambda x: x[0]/x[1]))
        Q.W = tmp.T
        return Q

    def _GetSubset(self):
        """
        AWGN通信路のdegradingに必要なyの部分集合を返すメソッド\n
        戻り値: yの部分集合の開始と終了位置を要素に持つリストをmu//2個まとめたリスト
        """
        y_max = 4               #yの最大値（ほんとは無限大）
        Division_num = 1000      #n,n+1間の分割数（ほんとは連続してる）
        y_range = [(1/Division_num)*i for i in range(y_max *  Division_num + 1)]    #yの値を保持するリスト（ほんとのyは連続）
        lambda_ = [np.exp(2*y/self.variance) for y in y_range]                      #各yに対する尤度比λ
        def C(x): return 1-(x/(x+1))*np.log2(1+1/x) - (1/(x+1))*np.log2(x+1)
        Capacity = [C(lam) for lam in lambda_]      #各λに対するC 
        data = dict(zip(Capacity, y_range))

        # 確認用 C[λ]のプロット
        # plt.plot(y_range, Capacity)
        # plt.yticks(np.arange(0, 1+0.01, 0.25))
        plt.show()
        nu = self.mu//2
        Separator_C = [i/nu for i in range(nu + 1)] #C[λ]の区切り位置

        #A_iを構成するyの区切りを習得
        Separator_y = [None]*(nu+1)
        Separator_y[0] = 0
        for i in range(1, nu+1):
            c = self._getNearestValue(Capacity, Separator_C[i])
            Separator_y[i] = data[c]
        # print(Separator_y)

        A_i = [None]*(nu)
        for i in range(nu):
            A_i[i] = [Separator_y[i], Separator_y[i+1]]
        
        return A_i

    def _getNearestValue(self, list_, num):
        """
        リストからある値に最も近い値を返却する関数\n
        list_: データ配列\n
        num: 対象値\n
        戻り値: 対象地に最も近いデータ配列内の値
        """
        # リスト要素と対象値の差分を計算し最小値のインデックスを取得
        idx = np.abs(np.asarray(list_) - num).argmin()
        return list_[idx]



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

    a = degrading_merge_AWGN(1, 0.5, 1024)
    Q = a.merge()
    
    print(Q.N)
    I_W = getSymmetricChannelCapacity(Q)
    print(I_W)

