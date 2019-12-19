import numpy as np
from CaliculateW import CalculateW_BSC
from CaliculateW import CalculateW_BEC
from decimal import Decimal
from Encoder import GetInformationIndex
from Encoder import GetGeneratorMatrix


class Decoder:
    def __init__(self, K, N, chaneloutput, chaneltype, path, checker=True):
        """
        デコーダクラスの初期化
        K:メッセージ長
        N:符号長
        chaneloutput: 0,1の通信路出力
        chaneltype: 通信路の種類
        path: 相互情報量の小さい順にインデックスを並べたファイルのパス
        checker: メッセージもどきを表示するか否か
        """
        self.K = K
        self.hat_message = np.array([])         #推定したメッセージを格納
        self.N = N
        self.hat_message_prime = np.array([])   #推定したメッセージもどきを格納
        self.chaneloutput = chaneloutput
        self.chaneltype = chaneltype            #通信路の種類を指定
        self.path = path
        self.checker = checker

    def DecodeOutput(self, P):
        """
        符号語推定値を通信路出力から推定する
        P: 誤り確率
        """
        estimatedcodeword = np.array([], dtype=np.uint8)
        informationindex = GetInformationIndex(self.K, self.path)
        matrixP = np.full((self.N,  int(np.log2(self.N))+1, 2), Decimal("-1"))
        # 事後確率の値を格納する配列
        j = 0
        for i in range(self.N):
            if i == informationindex[j]:
                hat_ui = self.EstimateCodeword_ibit(
                    P, self.N, self.chaneloutput, i, estimatedcodeword, matrixP)
                j += 1
            else:
                hat_ui = 0
            estimatedcodeword = np.insert(estimatedcodeword, i, hat_ui)

        self.hat_message_prime = estimatedcodeword

    def EstimateCodeword_ibit(self, P, N, chaneloutput, i, estimatedcodeword, matrixP):
        """
        符号語のibit目を求める
        """
        if self.chaneltype=="BSC":
            W_0 = CalculateW_BSC(P, N, chaneloutput, i, np.array([0]), estimatedcodeword, matrixP, 0)
            W_1 = CalculateW_BSC(P, N, chaneloutput, i, np.array([1]), estimatedcodeword, matrixP, 0)
            return 0 if W_0 >= W_1 else 1
        elif self.chaneltype=="BEC":
            W_0 = CalculateW_BEC(P, N, chaneloutput, i, np.array([0]), estimatedcodeword, matrixP, 0)
            W_1 = CalculateW_BEC(P, N, chaneloutput, i, np.array([1]), estimatedcodeword, matrixP, 0)
            return 0 if W_0 >= W_1 else 1
        else:
            exit(1)

    def DecodeMessage(self, P):
        """
        メッセージを符号語から復元
        K: メッセージ長
        path: インデックスを小さい順に並べたファイルのパス
        """
        self.DecodeOutput(P)
        if self.checker == True:
            print("メッセージもどき推定値:\t", self.hat_message_prime)
        
        informationindex = np.sort(GetInformationIndex(self.K, self.path)[:self.K])
        j = 0
        message = np.array([], dtype=np.uint8)

        for i in range(self.N):
            if i == informationindex[j]:
                message_j = self.hat_message_prime[i]
                message = np.insert(message, j, message_j)
                j += 1
                if j > self.K-1:
                    j = self.K-1
        self.hat_message = message


if __name__ == "__main__":
    if False:
        K = 16
        N = 32
        path = "./sort_I/sort_I_5_0.11_20.dat"
        chaneloutput = np.array([0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 1,
                             1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1])

        decoder0 = Decoder(K, N, chaneloutput, "BSC", path)
        #decoder0.DecodeOutput(0.11)
        decoder0.DecodeMessage(0.11)

       #    print(decoder0.hat_message_prime)
        print(decoder0.hat_message)

    if True:
        K =8
        N = 16
        e = 0.5
        path = "./sort_I/sortI_BEC_0.5_16.dat"
        chaneloutput2 = np.array([1 ,3, 0, 3, 0, 0, 0, 3, 3, 1, 3, 3, 3, 1, 0, 3])

        decoder1 = Decoder(K,N, chaneloutput2, "BEC", path)
        decoder1.DecodeMessage(e)

        print(decoder1.hat_message)