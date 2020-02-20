import numpy as np
from CaliculateW import CalculateW_BSC_2
from BMSchannel import BMSchannel





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
    def __init__(self, W, mu):
        """
        degrading_mergeに関するクラス\n
        W:元の通信路に関するBMSchannelクラス, mu:degradingした通信路の最大出力数 
        """
        self.W = W
        self.mu = mu
        self.data_list = []
        if type(W) is not BMSchannel:
            raise TypeError("BMSchannelクラスを使用してね")
        for i in range(1, W.N//2):
            d = _deg_data()

        


if __name__ == "__main__":
    pass
