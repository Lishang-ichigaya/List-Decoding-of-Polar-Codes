# -*- coding: utf-8 -*-
import numpy as np
import time


class Encoder:
    def __init__(self, k, n, path):
        """
        メッセージを符号化するクラス。\n
        k: メッセージ長\n
        n: 符号長\n
        path: インデックスを相互情報量が小さい順に並べたファイルのパス
        """
        self.k = k
        self.n = n
        self.path = path

    def Encode(self, message):
        """
        メッセージを符号化するメソッド\n
        message: 符号化したいメッセージ\n
        戻り値: 符号語
        """
        informationindex = self._GetInformationIndex()
        middle_message = np.zeros([self.n], dtype=np.uint8)
        middle_message[informationindex] = message  # 中間メッセージの作成
        # print("中間メッセージ:", middle_message)

        codeword = np.dot(middle_message, self._GetGeneratorMatrix()) % 2
        # codeword = codeword.A1
        return codeword

    def _GetInformationIndex(self):
        """
        情報ビットに対応するインデックス集合（情報インデックス）を得るメソッド
        戻り値: 情報インデックス
        """
        informationindex = np.loadtxt(self.path, dtype=np.uint16)
        # N = 65536 までは耐えられるようにunit16を使う
        # unit8 だとN=256までしか使えない
        informationindex = np.flip(informationindex)
        # 相互情報量の小さい順に、インデックスを並べ替えたものを外部で用意しておく
        return np.sort(informationindex[:self.k])

    def _GetGeneratorMatrix(self):
        """
        ポーラ符号の生成行列を作成するメソッド\n
        戻り値: 生成行列G_n
        """
        m = int(np.log2(self.n))

        # matrixF = np.array([[1, 0], [1, 1]], dtype=np.uint8)
        # matrixG = matrixF
        # for i in range(1, m):
        #     tmp = matrixG
        #     matrixG = np.dot(
        #         self._BuildPermutationMatrix(i+1),
        #         np.kron(matrixF, tmp)
        #     )

        matrixG = np.loadtxt("./G/G_"+str(m)+".txt", dtype=np.uint8)

        return matrixG

    def _BuildPermutationMatrix(self, m):
        """
        偶数番目を前に、奇数番目を後ろに置き換える行列を得るメソッド\n
        戻り値: 並べ替え行列B_n\n
        例:\n
        [1,0,0,0]  [1,0,0,0]\n
        [0,1,0,0]->[0,0,1,0]\n
        [0,0,1,0]  [0,1,0,0]\n
        [0,0,0,1]  [0,0,0,1]
        """
        if m == 1:
            matrixR = np.identity(1, dtype=np.uint8)
        else:
            matrixI_2 = np.identity(2, dtype=np.uint8)
            matrixR = np.identity(2, dtype=np.uint8)
            for _ in range(m-1):
                matrixR = np.kron(matrixI_2, matrixR)
            matrixEven = matrixR[::2]
            matrixOdd = matrixR[1::2]
            matrixR = np.concatenate([matrixEven, matrixOdd]).T
        return matrixR


if __name__ == "__main__":
    # chaneltype = "AWGN"
    # M = 8
    # R = 0.5
    # snr = 2
    # path = "./sort_I/"+chaneltype+"/sort_I_"+chaneltype+"_"+str(M)+"_"+str(R)+"_"+str(snr)+"_.dat"
    # a = Encoder(128, 256, path)
    # message = np.full(128, 1)
    # b = a.Encode(message)
    # print(b)
    n = 2048
    k = n//2
    enc = Encoder(k, n, "")
    G = enc._GetGeneratorMatrix()
    path_w = "G_"+str(int(np.log2(n)))+".txt"

    s = time.time()
    G_a = np.loadtxt(path_w, dtype=np.uint8)
    e = time.time()
    print("実行時間", e-s)

    np.set_printoptions(threshold=np.inf)
    np.set_printoptions(linewidth=np.inf)
    # np.savetxt("G_"+str(int(np.log2(n)))+".txt", G,fmt="%d")
    # print(G)
