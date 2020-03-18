# from decimal import Decimal
from CRC import CRC_Detector
from CaliculateW_awgn import CaliculateW_awgn
from Encoder import GetGeneratorMatrix
from Encoder import GetInformationIndex
from Encoder import GetParitybitIndex
import numpy as np
import copy
from tkinter import messagebox
import time

class ListDecoder:
    def __init__(self, K, N, L, chaneloutput, chaneltype, path, checker=True):
        """
        デコーダクラスの初期化
        K:メッセージ長
        N:符号長
        L:リストサイズ
        chaneloutput: 通信路出力
        chaneltype: 通信路の種類
        path: 相互情報量の小さい順にインデックスを並べたファイルのパス
        checker: メッセージもどきを表示するか否か
        """
        self.K = K
        self.hat_message = np.array([], dtype=np.uint8)  # 推定したメッセージを格納
        self.N = N
        self.L = L
        self.matrixP = np.full(
            (L, self.N,  int(np.log2(self.N))+1, 2), -1.0)
        # 各リストにおける事後確率の値を格納する配列
        # marixP[L][N][M][2]
        self.hat_message_list = [np.array([], dtype=np.uint8)] * L
        # 推定したメッセージもどきのリストを格納する配列
        self.activePath = [False] * L
        # アクティブなパスを示す配列。
        self.chaneloutput = chaneloutput
        self.chaneltype = chaneltype  # 通信路の種類を指定
        self.path = path
        self.checker = checker

    def _DecodeOutput(self, snr, R):
        informationindex = GetInformationIndex(self.K, self.path)
        j = 0
        self.activePath[0] = True
        # アクティブなパスを示す配列の0番目だけ初期化
        tmp_list = [np.array([], dtype=np.uint8)] * (2*self.L)
        tmp_W = np.full((2 * self.L), -1.0)
        tmp_matrixP = np.full((self.L, self.N,  int(np.log2(self.N))+1, 2), -1.0)
        tmp_activePath = [False] * (2 * self.L)
        variance = 10**(-snr/10)/(2*R)
        
        if self.chaneltype != "AWGN":
            raise ValueError("チャネルのタイプが違います")

        for i in range(self.N):
            if i == informationindex[j]:
                for l in range(self.L):
                    if self.activePath[l] == True:
                        tmp_list[2*l] = np.insert(self.hat_message_list[l], i, 0)
                        tmp_list[2*l + 1] = np.insert(self.hat_message_list[l], i, 1)
                        tmp_activePath[2*l] = True
                        tmp_activePath[2*l + 1] = True
                        tmp_W[2*l] = CaliculateW_awgn(variance, self.N, self.chaneloutput, i, np.array(
                            [0], dtype=np.uint8), self.hat_message_list[l], self.matrixP[l], 0)
                        tmp_W[2*l + 1] = CaliculateW_awgn(variance, self.N, self.chaneloutput, i, np.array(
                            [1], dtype=np.uint8), self.hat_message_list[l], self.matrixP[l], 0)
                        tmp_matrixP[l] = self.matrixP[l]
                        #print(tmp_list[2*l], tmp_W[2*l])
                        #print(tmp_list[2*l+1], tmp_W[2*l+1])
                        #print(tmp_W[2*l], ",", tmp_W[2*l+1])
                # ここまでで全てのパスを2倍に複製し、各々の事後確率を計算した。
                sort_W_index = np.argsort(tmp_W)
                sort_W_index = sort_W_index[-1::-1]
                sort_W_index = sort_W_index[:self.L]
                # print(sort_W_index)
                # 事後確率が大きいL個のインデックスを取り出した
                for l in range(self.L):
                    if tmp_activePath[sort_W_index[l]] == True:
                        self.hat_message_list[l] = tmp_list[sort_W_index[l]]
                        self.matrixP[l] = tmp_matrixP[sort_W_index[l]//2]
                        # print(self.hat_message_list[l])
                        self.activePath[l] = True
                j += 1
            else:
                for l in range(self.L):
                    if self.activePath[l] == True:
                        self.hat_message_list[l] = np.insert(self.hat_message_list[l], i, 0)
            # print(self.hat_message_list)
        # ここまででメインの処理はおわり

        if self.checker:
            print("最終的な候補")
            for l in range(self.L):
                print(self.hat_message_list[l])

        self.hat_message_prime = self.hat_message_list[0]

    def DecodeMessage(self, snr, R):
        """
        メッセージを通信路出力から復号
        snr: E_b/N_0で定義されれるSN比\n
        R: 符号化レート
        """
        self._DecodeOutput(snr, R)
        if self.checker:
            print("SCLメッセージ？推定値:\t", self.hat_message_prime)

        informationindex = np.sort(GetInformationIndex(self.K, self.path)[:self.K])
        j = 0
        message = self.hat_message_prime[informationindex]
        # メッセージの取り出し
        self.hat_message = message




if __name__ == "__main__":
    pass
    # if True:
    #     K = 36
    #     N = 64
    #     L = 4
    #     path = "./sort_I/sort_I_6_0.11_20.dat"
    #     chaneloutput = np.array([0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0,
    #                              0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1])

    #     decoder0 = ListDecoder_F(K, N, L, chaneloutput, "BSC", path, False)
    #     decoder0.DecodeMessage(0.06)
    #     print("SCL: ", decoder0.hat_message)

    #     # decoder1 = DecoderW(K, N, chaneloutput, "BSC", path, False)
    #     # decoder1.DecodeMessage(0.06)
    #     # print(" SC: ", decoder1.hat_message)
    #     # print("Ans:  [0 0 1 1 0 0 0 0 1 1 1 0 1 0 0 1]")
    # if False:
    #     K = 8
    #     N = 16
    #     e = 0.5
    #     path = "./sort_I/sortI_BEC_0.5_16.dat"
    #     chaneloutput2 = np.array(
    #         [1, 3, 0, 3, 0, 0, 0, 3, 3, 1, 3, 3, 3, 1, 0, 3])

    #     decoder1 = ListDecoder(K, N, L, chaneloutput2, "BEC", path)
    #     decoder1.DecodeMessage(e)

    #     print(decoder1.hat_message)