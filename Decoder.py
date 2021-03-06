from CaliculateLR import CalculateLR_BEC_2
from CaliculateLR import CalculateLR_BEC
from CaliculateLR import CalculateLR_BSC
from Encoder import GetGeneratorMatrix
from Encoder import GetInformationIndex
import numpy as np
from CaliculateW import CalculateW_BSC
from CaliculateW import CalculateW_BSC_2
from CaliculateW import CalculateW_BEC
from CaliculateW import CalculateW_BEC_2
from CRC import CRC_Detector
from decimal import Decimal
from decimal import getcontext
getcontext().prec = 28


class ListDecoder_F:
    def __init__(self, K, N, L, chaneloutput, chaneltype, path, checker=True):
        """
        デコーダクラスの初期化
        K:メッセージ長
        N:符号長
        L:リストサイズ
        chaneloutput: 0,1の通信路出力
        chaneltype: 通信路の種類
        path: 相互情報量の小さい順にインデックスを並べたファイルのパス
        checker: メッセージもどきを表示するか否か
        """
        self.K = K
        self.hat_message = np.array([], dtype=np.uint8)  # 推定したメッセージを格納
        self.N = N
        self.L = L
        self.matrixP = np.full(
            (L, self.N,  int(np.log2(self.N))+1, 2), Decimal("-1"))
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

    def DecodeOutput(self, P):
        """
        符号語推定値を通信路出力から推定する
        P: 誤り確率
        """
        #estimatedcodeword = np.array([], dtype=np.uint8)
        informationindex = GetInformationIndex(self.K, self.path)
        j = 0
        self.activePath[0] = True
        # アクティブなパスを示す配列の0番目だけ初期化
        tmp_list = [np.array([], dtype=np.uint8)] * (2*self.L)
        tmp_W = np.full((2 * self.L), Decimal("-1"))
        tmp_matrixP = np.full((self.L, self.N,  int(np.log2(self.N))+1, 2), Decimal("-1"))
        tmp_activePath = [False] * (2 * self.L)
        if self.chaneltype == "BSC":
            for i in range(self.N):
                # print("--------------------"+str(i)+"--------------------")
                if i == informationindex[j]:
                    for l in range(self.L):
                        if self.activePath[l] == True:
                            tmp_list[2*l] = np.insert(self.hat_message_list[l], i, np.array([0]))
                            tmp_list[2*l + 1] = np.insert(self.hat_message_list[l], i, np.array([1]))
                            tmp_activePath[2*l] = True
                            tmp_activePath[2*l + 1] = True
                            tmp_W[2*l] = CalculateW_BSC(P, self.N, self.chaneloutput, i, np.array(
                                [0], dtype=np.uint8), self.hat_message_list[l], self.matrixP[l], 0)
                            tmp_W[2*l + 1] = CalculateW_BSC(P, self.N, self.chaneloutput, i, np.array(
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
                            self.matrixP[l] = tmp_matrixP[int(sort_W_index[l]/2)]
                            # print(self.hat_message_list[l])
                            self.activePath[l] = True
                    j += 1
                else:
                    for l in range(self.L):
                        if self.activePath[l] == True:
                            self.hat_message_list[l] = np.insert(self.hat_message_list[l], i, np.array([0]))
                # print(self.hat_message_list)
            # ここまででメインの処理はおわり

        if self.chaneltype == "BEC":
            for i in range(self.N):
                if i == informationindex[j]:
                    for l in range(self.L):
                        if self.activePath[l] == True:
                            tmp_list[2*l] = np.insert(self.hat_message_list[l], i, np.array([0]))
                            tmp_list[2*l + 1] = np.insert(self.hat_message_list[l], i, np.array([1]))
                            tmp_activePath[2*l] = True
                            tmp_activePath[2*l + 1] = True
                            tmp_W[2*l] = CalculateW_BEC(P, self.N, self.chaneloutput, i, np.array(
                                [0], dtype=np.uint8), self.hat_message_list[l], self.matrixP[l], 0)
                            tmp_W[2*l + 1] = CalculateW_BEC(P, self.N, self.chaneloutput, i, np.array(
                                [1], dtype=np.uint8), self.hat_message_list[l], self.matrixP[l], 0)
                            tmp_matrixP[l] = self.matrixP[l]
                        # パスを2倍にして、確率の計算
                    sort_W_index = np.argsort(tmp_W)
                    sort_W_index = sort_W_index[-1::-1]
                    sort_W_index = sort_W_index[:self.L]
                    # 事後確率が大きいL個のインデックスを取り出した
                    for l in range(self.L):
                        if tmp_activePath[sort_W_index[l]] == True:
                            self.hat_message_list[l] = tmp_list[sort_W_index[l]]
                            self.matrixP[l] = tmp_matrixP[int(sort_W_index[l]/2)]
                            self.activePath[l] = True
                    j += 1
                else:
                    for l in range(self.L):
                        if self.activePath[l] == True:
                            self.hat_message_list[l] = np.insert(self.hat_message_list[l], i, np.array([0]))
            # ここまででメインの処理はおわり

        if self.checker:
            print("最終的な候補")
            for l in range(self.L):
                print(self.hat_message_list[l])

        self.hat_message_prime = self.hat_message_list[0]

    def DecodeMessage(self, P):
        """
        メッセージを符号語から復元
        P: 誤り確率
        """
        self.DecodeOutput(P)
        if self.checker == True:
            print("SCLメッセージ？推定値:\t", self.hat_message_prime)

        informationindex = np.sort(
            GetInformationIndex(self.K, self.path)[:self.K])
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


class ListDecoder_CRC(ListDecoder_F):
    def __init__(self, K, N, L, chaneloutput, chaneltype, path, checker=True):
        super().__init__(K, N, L, chaneloutput, chaneltype, path, checker)

    def DecodeMessage(self, P):
        """
        メッセージを符号語から復元
        P: 誤り確率
        """
        self.DecodeOutput(P)

        informationindex = np.sort(GetInformationIndex(self.K, self.path)[:self.K])
        is_nocrc = True
        likelypass = self.hat_message_list[0]

        for l in range(self.L):
            j = 0
            message = np.array([], dtype=np.uint8)
            for i in range(self.N):
                if i == informationindex[j]:
                    message_j = self.hat_message_list[l][i]
                    message = np.insert(message, j, message_j)
                    j += 1
                    if j > self.K-1:
                        j = self.K-1
            crcdec = CRC_Detector(message)
            if crcdec.IsNoError():
                #CRCが一致した場合の操作
                is_nocrc = False
                #print("\t\t",l,"-----------------------------------------------")
                #print("\t\t\t",message)
                self.hat_message= message
                break
            #print(l)

        if is_nocrc:
            #CRCが一つも一致しない場合の操作
            for i in range(self.N):
                if i == informationindex[j]:
                    message_j = likelypass[i]
                    message = np.insert(message, j, message_j)
                    j += 1
                    if j > self.K-1:
                        j = self.K-1
            self.hat_message = message



class ListDecoder:
    def __init__(self, K, N, L, chaneloutput, chaneltype, path, checker=True):
        """
        デコーダクラスの初期化
        K:メッセージ長
        N:符号長
        L:リストサイズ
        chaneloutput: 0,1の通信路出力
        chaneltype: 通信路の種類
        path: 相互情報量の小さい順にインデックスを並べたファイルのパス
        checker: メッセージもどきを表示するか否か
        """
        self.K = K
        self.hat_message = np.array([], dtype=np.uint8)  # 推定したメッセージを格納
        self.N = N
        self.L = L
        self.matrixP = np.full(
            (L, self.N,  int(np.log2(self.N))+1, 2), Decimal("-1"))
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

    def DecodeOutput(self, P):
        """
        符号語推定値を通信路出力から推定する
        P: 誤り確率
        """
        #estimatedcodeword = np.array([], dtype=np.uint8)
        informationindex = GetInformationIndex(self.K, self.path)
        j = 0
        self.activePath[0] = True
        # アクティブなパスを示す配列の0番目だけ初期化

        tmp_list = [np.array([], dtype=np.uint8)] * (2*self.L)
        tmp_W = np.full((2 * self.L), Decimal("-1"))
        tmp_activePath = [False] * (2*self.L)
        for i in range(self.N):
            if i == informationindex[j]:
                for l in range(self.L):
                    if self.activePath[l] == True:
                        tmp_list[2*l] = np.insert(self.hat_message_list[l],
                                                  i, np.array([0]))
                        tmp_list[2*l +
                                 1] = np.insert(self.hat_message_list[l], i, np.array([1]))
                        tmp_activePath[2*l] = True
                        tmp_activePath[2*l + 1] = True
                        tmp_W[2*l] = CalculateW_BSC_2(P, self.N, self.chaneloutput, i, np.array(
                            [0], dtype=np.uint8), self.hat_message_list[l])
                        tmp_W[2*l + 1] = CalculateW_BSC_2(P, self.N, self.chaneloutput, i, np.array(
                            [1], dtype=np.uint8), self.hat_message_list[l])
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
                        # print(self.hat_message_list[l])
                        self.activePath[l] = True
                j += 1

            else:
                for l in range(self.L):
                    if self.activePath[l] == True:
                        self.hat_message_list[l] = np.insert(
                            self.hat_message_list[l], i, np.array([0]))

            # print(self.hat_message_list)
        # ここまででメインの処理はおわり？

        if self.checker:
            print("最終的な候補")
            for l in range(self.L):
                print(self.hat_message_list[l])

        self.hat_message_prime = self.hat_message_list[0]

    def DecodeMessage(self, P):
        """
        メッセージを符号語から復元
        P: 誤り確率
        """
        self.DecodeOutput(P)
        if self.checker == True:
            print("SCLメッセージ？推定値:\t", self.hat_message_prime)

        informationindex = np.sort(
            GetInformationIndex(self.K, self.path)[:self.K])
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


class DecoderW:
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
        self.hat_message = np.array([])  # 推定したメッセージを格納
        self.N = N
        self.hat_message_prime = np.array([])  # 推定したメッセージもどきを格納
        self.chaneloutput = chaneloutput
        self.chaneltype = chaneltype  # 通信路の種類を指定
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
        if self.chaneltype == "BSC":
            for i in range(self.N):
                W_0 = CalculateW_BSC(P, self.N, self.chaneloutput, i, np.array(
                    [0], dtype=np.uint8), estimatedcodeword, matrixP, 0)
                W_1 = CalculateW_BSC(P, self.N, self.chaneloutput, i, np.array(
                    [1], dtype=np.uint8), estimatedcodeword, matrixP, 0)
                if i == informationindex[j]:
                    hat_ui = 0 if W_0 > W_1 else 1
                    j += 1
                else:
                    hat_ui = 0
                estimatedcodeword = np.insert(estimatedcodeword, i, hat_ui)

        if self.chaneltype == "BEC":
            for i in range(self.N):
                W_0 = CalculateW_BEC(P, self.N, self.chaneloutput, i, np.array(
                    [0], dtype=np.uint8), estimatedcodeword, matrixP, 0)
                W_1 = CalculateW_BEC(P, self.N, self.chaneloutput, i, np.array(
                    [1], dtype=np.uint8), estimatedcodeword, matrixP, 0)
                if i == informationindex[j]:
                    hat_ui = 0 if W_0 > W_1 else 1
                    j += 1
                else:
                    hat_ui = 0
                estimatedcodeword = np.insert(estimatedcodeword, i, hat_ui)

        self.hat_message_prime = estimatedcodeword

    def DecodeMessage(self, P):
        """
        メッセージを符号語から復元
        K: メッセージ長
        path: インデックスを小さい順に並べたファイルのパス
        """
        self.DecodeOutput(P)
        if self.checker == True:
            print(" SCメッセージ？推定値:\t", self.hat_message_prime)

        informationindex = np.sort(
            GetInformationIndex(self.K, self.path)[:self.K])
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


class DecoderLR:
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
        self.hat_message = np.array([])  # 推定したメッセージを格納
        self.N = N
        self.hat_message_prime = np.array([])  # 推定したメッセージもどきを格納
        self.chaneloutput = chaneloutput
        self.chaneltype = chaneltype  # 通信路の種類を指定
        self.path = path
        self.checker = checker

    def DecodeOutput(self, P):
        """
        符号語推定値を通信路出力から推定する
        P: 誤り確率
        """
        estimatedcodeword = np.array([], dtype=np.uint8)
        informationindex = GetInformationIndex(self.K, self.path)
        matrixP = np.full((self.N,  int(np.log2(self.N))+1), Decimal("-1"))
        # 事後確率の値を格納する配列
        j = 0
        for i in range(self.N):
            if self.chaneltype == "BSC":
                LR = CalculateLR_BSC(
                    P, self.N, self.chaneloutput, i, estimatedcodeword, matrixP, 0)
            elif self.chaneltype == "BEC":
                LR = CalculateLR_BEC(
                    P, self.N, self.chaneloutput, i, estimatedcodeword, matrixP, 0)
                #LR = CalculateLR_BEC_2(P, self.N, self.chaneloutput, i, estimatedcodeword)

            if i == informationindex[j]:
                # print(i,type(LR),LR)
                # if False and i==self.N-1:
                #    with open("yuudohi.csv",mode='a') as f:
                #        for k in range(self.N):
                #            for l in range(int(np.log2(self.N))+1)[::-1]:
                #                f.write(str(matrixP[k][l])+", ")
                #            if k in informationindex:
                #                f.write("★, ")
                #            f.write("\n")
                hat_ui = 0 if LR > 1 else 1
                j += 1
            else:
                hat_ui = 0
            estimatedcodeword = np.insert(estimatedcodeword, i, hat_ui)

        self.hat_message_prime = estimatedcodeword

    def DecodeMessage(self, P):
        """
        メッセージを符号語から復元
        K: メッセージ長
        path: インデックスを小さい順に並べたファイルのパス
        """
        self.DecodeOutput(P)
        if self.checker == True:
            print(" SCメッセージ？推定値:\t", self.hat_message_prime)

        informationindex = np.sort(
            GetInformationIndex(self.K, self.path)[:self.K])
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
    if True:
        K = 16
        N = 32
        L = 16
        path = "./sort_I/sort_I_5_0.11_20.dat"
        chaneloutput = np.array([1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0,
                                 1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1])

        decoder0 = ListDecoder(K, N, L, chaneloutput, "BSC", path, False)
        decoder0.DecodeMessage(0.11)
        print("SCL: ", decoder0.hat_message)

        decoder1 = DecoderW(K, N, chaneloutput, "BSC", path, False)
        decoder1.DecodeMessage(0.11)
        print(" SC: ", decoder1.hat_message)
        print("Ans:  [0 0 1 1 0 0 0 0 1 1 1 0 1 0 0 1]")
    if False:
        K = 8
        N = 16
        e = 0.5
        path = "./sort_I/sortI_BEC_0.5_16.dat"
        chaneloutput2 = np.array(
            [1, 3, 0, 3, 0, 0, 0, 3, 3, 1, 3, 3, 3, 1, 0, 3])

        decoder1 = ListDecoder(K, N, L, chaneloutput2, "BEC", path)
        decoder1.DecodeMessage(e)

        print(decoder1.hat_message)
