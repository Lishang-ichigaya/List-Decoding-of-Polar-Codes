import numpy as np
from scipy.stats import norm
from CRC import CRC_Detector
import copy


class LLR_SCDecoder:
    def __init__(self, k, n, snr, path):
        """
        受信系列を復号するクラス\n
        k: メッセージ長\n
        n: 符号長\n
        snr: ビットあたりのSN比（E_b/N_0)\n
        path: インデックスを相互情報量が小さい順に並べたファイルのパス
        """
        self.k = k
        self.n = n
        self.N_0 = 10**(-snr/10)/(2*(k/n))
        self.path = path

        self.informationindex = self._GetInformationIndex()
        self.channeloutput = None
        self.decoded_middle_message = [np.array([], dtype=np.uint8)]
        self.calculatedLLR = np.full(
            (self.n,  int(np.log2(self.n))+1), None)

    def Decode(self, channeloutput):
        """
        受信系列をSC復号するメソッド\n
        channeloutput: AWGNチャネルからの受信系列\n
        """
        self.channeloutput = channeloutput

        self._DecodeMiddleMessage()
        # print("中間メッセージSC:\n", self.decoded_middle_message)
        decoded_message = self.decoded_middle_message[self.informationindex]
        return decoded_message

    def _DecodeMiddleMessage(self):
        """
        情報ビットと凍結ビットが含まれた中間メッセージをL個復号するメソッド\n
        """
        for i in range(self.n):
            if i in self.informationindex:
                LLR = self._CalculateLLR(
                    self.decoded_middle_message, i, self.calculatedLLR)
                u_i = 0 if LLR > 0 else 1
                self.decoded_middle_message = np.append(
                    self.decoded_middle_message, u_i)
            else:
                self.decoded_middle_message = np.append(
                    self.decoded_middle_message, 0)

    def _CalculateLLR(self, middle_message, i, calculatedLLR):
        """
        現在までの中間メッセージ推定値をもとに、次の値がu_iであるときの尤度を計算するメソッド\n
        middle_message: 現在までの中間メッセージ推定値
        calculated++R: 計算済みのLLRを格納してある配列
        i: 尤度を計算するインデックス
        """

        def get_LLR(n, chaneloutput, i,  middle_message, calculatedLLR, branch):
            """
            LLR(y^n,u^i-1|u_i)を計算する\n
            n: 符号長\n
            chaneloutpuy: 通信路出力\n
            i: 推定したいビットのインデックス\n
            middle_message: 現在までに推定された符号語ビット列\n
            calculatedLLR: 計算済みの尤度を保持する N*logN*2 の行列\n
            branch: Tal,Vardyの論文中に出てくるブランチ\n
            """
            m = int(np.log2(n))
            if calculatedLLR[i + n * branch][m] != None:
                # 計算済みのW
                return calculatedLLR[i + n * branch][m]

            if m == 0:
                # 再起の終了条件
                W_0 = np.log(norm.pdf(x=chaneloutput, loc=+
                                      1, scale=np.sqrt(self.N_0)))
                W_1 = np.log(norm.pdf(x=chaneloutput, loc=-
                                      1, scale=np.sqrt(self.N_0)))
                LLR_0 = W_0 - W_1
                calculatedLLR[i + n * branch][m] = LLR_0
                return LLR_0

            # 以下再起的呼び出し
            y_1 = chaneloutput[:n//2]
            y_2 = chaneloutput[n//2:]

            hat_u1, hat_u2 = None, None
            if i > 1:
                # uが存在するときの操作

                hat_u_of_i_minus_1 = middle_message[i-1]
                # i-1番目の中間メッセージ推定値を抜き出す
                j = i if i % 2 == 0 else i-1
                middle_message = middle_message[:j]
                # i が偶数番目か奇数番目かを判定する

                # 偶数と奇数に分解
                hat_u1 = middle_message[::2]
                hat_u2 = middle_message[1::2]

                hat_u1 = hat_u1 ^ hat_u2
                hat_u2 = hat_u2

            else:
                # uが存在しないときのそうさ
                if i == 1:
                    hat_u_of_i_minus_1 = middle_message[0]
                j = 0
                hat_u1 = np.array([], dtype=np.uint8)
                hat_u2 = np.array([], dtype=np.uint8)

            # Arikanが提案した再起式に従って、再帰的に計算。
            if i % 2 == 0:
                LLR_1 = get_LLR(n//2, y_1, j//2, hat_u1,
                                calculatedLLR, 2*branch)
                LLR_2 = get_LLR(n//2, y_2, j//2, hat_u2,
                                calculatedLLR, 2*branch+1)
                LLR = np.sign(LLR_1) * np.sign(LLR_2) * min(abs(LLR_1), abs(LLR_2)) #近似式
                # LLR = np.log((np.exp(LLR_1 + LLR_2)+1) /
                            #  (np.exp(LLR_1)+np.exp(LLR_2)))
            else:
                LLR_1 = get_LLR(n//2, y_1, j//2, hat_u1,
                                calculatedLLR, 2*branch)
                LLR_2 = get_LLR(n//2, y_2, j//2, hat_u2,
                                calculatedLLR, 2*branch+1)
                LLR = ((-1)**(hat_u_of_i_minus_1))*LLR_1 + LLR_2

            calculatedLLR[i + n * branch][m] = LLR
            return LLR

        y = self.channeloutput
        n = self.n
        u = middle_message
        P = calculatedLLR
        LLR = get_LLR(n, y, i, u, P, 0)
        # print(LLR)
        return LLR

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


class LLR_SCLDecoder(LLR_SCDecoder):
    def __init__(self, k, n, L, snr, path):
        """
        受信語を復号するクラス\n
        k: メッセージ長\n
        n: 符号長\n
        L: リストサイズ\n
        snr: ビットあたりのSN比（E_b/N_0)\n
        path: インデックスを相互情報量が小さい順に並べたファイルのパス\n
        """
        super().__init__(k, n, snr, path)
        self.L = L
        self.decoded_list = [np.array([], dtype=np.uint8)]
        self.PathMetric = [np.array([0], dtype=np.float64)]
        self.calculatedLLR = np.full(
            (self.L, self.n,  int(np.log2(self.n))+1), None)
        del(self.decoded_middle_message)

    def Decode(self, channeloutput):
        """
        受信系列からSCL復号を行うメソッド\n
        channeloutput: AWGNチャネルからの受信系列\n
        """
        self.channeloutput = channeloutput

        self._DecodeMiddleMessage()
        decoded_message = self._PickCorrectMessage()
        return decoded_message

    def _DecodeMiddleMessage(self):
        for i in range(self.n):
            if i in self.informationindex:
                l = 0
                tmp_calculatedLLR = self.calculatedLLR  # 計算済みのLLRを一旦保持
                tmp_PathMetric = self.PathMetric
                tmp_list = []  # PMとLLRと推定値を保持するためのリスト

                for lth_path in self.decoded_list:
                    lth_path_append_0 = np.append(lth_path, 0)
                    lth_path_append_1 = np.append(lth_path, 1)
                    
                    LLR = self._CalculateLLR(
                        lth_path, i, self.calculatedLLR[l])
                    PM0 = self._CalculatePathMetric(tmp_PathMetric[l], LLR, 0)
                    PM1 = self._CalculatePathMetric(tmp_PathMetric[l], LLR, 1)

                    tmp_list.append(
                        [lth_path_append_0, PM0, tmp_calculatedLLR[l]])
                    tmp_list.append(
                        [lth_path_append_1, PM1, tmp_calculatedLLR[l]])
                    # 後のソートのため[パス、PM、計算済みLLR]を要素とするリストを作る
                    l += 1
                tmp_list = sorted(tmp_list, key=lambda x: x[1])
                if len(tmp_list) > self.L:
                    tmp_list = tmp_list[:self.L]

                self.decoded_list = [x[0] for x in tmp_list]
                self.PathMetric = [x[1] for x in tmp_list]
                self.calculatedLLR = np.array([x[2] for x in tmp_list])
        
            else:
                l = 0
                for lth_path in self.decoded_list:
                    lth_path = np.append(lth_path, 0)
                    LLR = self._CalculateLLR(
                        lth_path, i, self.calculatedLLR[l])
                    PM = self._CalculatePathMetric(self.PathMetric[l], LLR, 0)
                    self.decoded_list[l] = lth_path
                    self.PathMetric[l] = PM
                    l += 1
            
    def _CalculatePathMetric(self, PM, LLR, u_i):
        """
        Path Metricを計算するメソッド\n
        PM: パスの1つ前までのPM\n
        LLR: パスのLLR\n
        u_i: パスのi番目の値\n
        戻り値: パスのPM\n
        """
        # newPM = PM + np.log(1+np.exp(-(1-2*u_i)*LLR))
        newPM = PM if u_i==0.5*(1-np.sign(LLR)) else PM+abs(LLR)
        return newPM

    def _PickCorrectMessage(self):
        # print("中間メッセージ推定値SCL:\n",self.decoded_list[0])
        return self.decoded_list[0][self.informationindex]


if __name__ == "__main__":
    # T = LLR_SCDecoder(4, 8, 0, 2, 5)
    pass
