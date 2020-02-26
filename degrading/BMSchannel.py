import numpy as np


class BMSchannel:
    def __init__(self, W, N):
        """
        BMSchannelの初期化\n
        W:通信路を表す行列(リスト).  N:通信路出力の総数( 例:5出力なら2^5=32 )
        """
        if len(W[0]) != len(W[1]):
            raise TypeError("適切なWを使用してね")
        self.W = np.array(W)
        self.N = N

    @classmethod
    def mul_sq(cls, W):
        if type(W) is not BMSchannel:
            raise TypeError("BMSchannelクラスを使う！”")

        empty_W = [[None] * (W.N*W.N) for i in range(2)]
        W_W = BMSchannel(empty_W, W.N*W.N)
        range_N = range(W.N)
        for u_1 in [0, 1]:
            for i in range_N:
                for j in range_N:
                    w_w = 0
                    for u_2 in [0, 1]:
                        w = W.W[(u_1+u_2) % 2][i] * W.W[u_2][j]
                        w_w += w
                    w_w *= 0.5
                    W_W.W[u_1][i*W.N + j] = w_w
        tmp = W_W.W.T
        tmp = np.array(sorted(tmp, key=lambda x: x[0]/x[1]))
        W_W.W = tmp.T
        return W_W

    @classmethod
    def mul_cir(cls, W):
        if type(W) is not BMSchannel:
            raise TypeError("BMSchannelクラスを使う！”")

        empty_W = [[None] * (W.N*W.N*2) for i in range(2)]
        W_W = BMSchannel(empty_W, W.N*W.N*2)
        range_N = range(W.N)
        for u_2 in [0, 1]:
            for i in range_N:
                for j in range_N:
                    for u_1 in [0, 1]:
                        w_w = 0.5*W.W[(u_1+u_2) % 2][i] * W.W[u_2][j]
                        W_W.W[u_2][i*W.N*2 + j*2 + u_1] = w_w
        tmp = W_W.W.T
        tmp = np.array(sorted(tmp, key=lambda x: x[0]/x[1]))
        W_W.W = tmp.T
        return W_W


if __name__ == "__main__":
    W = [[0.89, 0.11], [0.11, 0.89]]
    W_0 = BMSchannel(W, 2)

    W_1 = [None]*2
    W_2 = [None]*4
    W_3 = [None]*8
    W_4 = [None]*16
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


    I_8 = [None]*8
    for i in range(8):
        I = 0
        for x in [0, 1]:
            for y in range(W_3[i].N):
                I += W_3[i].W[x][y] * np.log2(W_3[i].W[x][y]/(W_3[i].W[0][y]+W_3[i].W[1][y]))
        I = 1+0.5*I
        I_8[i] = I
        print(I)

    # for I in I_8:
    #     print(I)