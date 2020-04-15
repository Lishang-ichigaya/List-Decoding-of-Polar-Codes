# -*- coding: utf-8 -*-
import numpy as np
from scipy.stats import norm 

class SCL_Decoder:
    def __init__(self, k, n, L, snr, path):
        """
        受信系列を復号するクラス\n
        k: メッセージ長\n
        n: 符号長\n
        snr: ビットあたりのSN比（E_b/N_0)\n
        path: インデックスを相互情報量が小さい順に並べたファイルのパス
        """
        self.k = k
        self.n = n
        self.L = L
        self.N_0 = 10**(-snr/10)/(2*(k/n))
        self.path = path

        self.channeloutput = None
        self.decoded_list = None

    def Decode(self, channeloutput):
        """
        受信系列を復号するメソッド\n
        channeloutput: AWGNチャネルからの受信系列
        """
        self.channeloutput = channeloutput

        self._DecodeMiddleMessage()
        decoded_message = self._SelectTrueMessage()
        return decoded_message

    def _DecodeMiddleMessage(self):
        """
        情報ビットと凍結ビットが含まれた中間メッセージをL個復号するメソッド\n
        """
        self.decoded_list = [[np.array([], dtype=np.uint8), -1]]
        #各リストは尤度と推定値を保持
        tmp_decoded_list = []

        for i in range(self.n):
            for lth_path in self.decoded_list:
                # if i番目が情報ビット
                path_0appended = np.append(lth_path[0], 0)
                path_1appended = np.append(lth_path[0], 1)
                # likehood_0appended = _CalculateLikelihood(lth_path[0], 0)
                # likehood_1appended = _CalculateLikelihood(lth_path[0], 1)
                # tmp_decoded_list.append([path_0appended, likehood_0appended])
                # tmp_decoded_list.append([path_1appended, likehood_1appended])
            
            # tmp_decoded_list = sorted(tmp_decoded_list, key=lambda x: x[1], reverse=True)
            
    def _SelectTrueMessage(self):
        """
        中間メッセージの復号完了後に、L個のリスト中から最も正しいと推定されるメッセージを求めるメソッド\n
        戻り値: 正しいと推定されるメッセージ
        """
        return 0

    def _GetMessage(self):
        """
        情報ビットと凍結ビットが含まれた中間メッセージからメッセージを抜き出すメソッド
        """
        pass

    def _CalculateLikelihood(self,u_i, i):
        def W_awgn(n, chaneloutput, i, u_i, estimatedcodeword_u, calculatedLikehood, branch):
            """
            入力がu_iであるときの事後確率W(y^n,u^i-1|u_i)を計算する
            N:符号長
            chaneloutpuy_y:通信路出力
            i:推定したいビット位置
            u_i: 0か1
            estimatedcodeword_u:現在までに推定された符号語ビット列
            matrixP: 事後確率を保持する N*logN*2 の行列
            """

            m = int(np.log2(n))
            if calculatedLikehood[i + n * branch][m][u_i[0]] != -1.0:
                # 計算済みのW
                return calculatedLikehood[i + n * branch][m][u_i[0]]

            if m == 0:
                # 再起の終了条件
                if u_i == 0:
                    W = norm.pdf(x=chaneloutput, loc=+1, scale=np.sqrt(self.N_0))
                else:
                    W = norm.pdf(x=chaneloutput, loc=-1, scale=np.sqrt(self.N_0))
                # matrixP[i + N * branch][M][u_i[0]] = W
                return W

            # 以下再起的呼び出し
            y_1 = chaneloutput[:n//2]
            y_2 = chaneloutput[n//2:]

            if i > 1:
                # uが存在するときの操作
                hat_u_i_minus_1 = estimatedcodeword_u[i-1]

                j = i if i % 2 == 0 else i-1
                # ⇔ j-1 = i-1 or i-2
                estimatedcodeword_u = estimatedcodeword_u[:j]

                # 偶数と奇数に分解
                hat_u1 = estimatedcodeword_u[::2]
                hat_u2 = estimatedcodeword_u[1::2]

                # 偶奇でxor、奇数はそのまま
                hat_u1 = hat_u1 ^ hat_u2
                hat_u2 = hat_u2
            else:
                # uが存在しないときのそうさ
                # ⇔ i<=1
                if i == 1:
                    hat_u_i_minus_1 = estimatedcodeword_u[0]
                j = 0
                hat_u1 = np.array([], dtype=np.uint8)
                hat_u2 = np.array([], dtype=np.uint8)

            # Arikanが提案した再起式に従って、再帰的に計算。
            if i % 2 == 0:
                # u_i+1が0と1の場合について和をとる
                u_i_puls_1 = np.array([0], dtype=np.uint8)
                W_1 = (0.5
                    * W_awgn(n//2, y_1, j//2, u_i ^ u_i_puls_1, hat_u1, calculatedLikehood, 2*branch)
                    * W_awgn(n//2, y_2, j//2, u_i_puls_1, hat_u2, calculatedLikehood, 2*branch+1))
                u_i_puls_1 = np.array([1], dtype=np.uint8)
                W_2 = (0.5
                    * W_awgn(n//2, y_1, j//2, u_i ^ u_i_puls_1, hat_u1, calculatedLikehood, 2*branch)
                    * W_awgn(n//2, y_2, j//2, u_i_puls_1, hat_u2, calculatedLikehood, 2*branch+1))
                W = W_1 + W_2
            else:
                W = (0.5
                    * W_awgn(n//2, y_1, j//2, hat_u_i_minus_1 ^ u_i, hat_u1, calculatedLikehood, 2*branch)
                    * W_awgn(n//2, y_2, j//2, u_i, hat_u2, calculatedLikehood, 2*branch+1))
            calculatedLikehood[i + n * branch][m][u_i[0]] = W
            return W

        y = [1.34514554, 0.51447536, -1.2354836, -0.33108537]
        n = 4
        k = 2
        i = 0
        u_i = np.array([1], dtype=np.uint8)
        u = np.array([], dtype=np.uint8)
        P = np.full((n, int(np.log2(n))+1, 2), -1.0)
        a = W_awgn(n, y, i, u_i, u, P, 0)
        print(a)
        
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

if __name__ == "__main__":
    d = SCL_Decoder(2, 4, 2, 2, "aa")
    d._CalculateLikelihood(8, 5)
    pass