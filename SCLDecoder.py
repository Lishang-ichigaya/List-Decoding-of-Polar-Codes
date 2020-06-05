# -*- coding: utf-8 -*-
import numpy as np
from scipy.stats import norm
from CRC import CRC_Detector
import copy


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
        self.r = 0
        self.N_0 = 10**(-snr/10)/(2*(k/n))
        self.path = path

        self.informationindex = None
        self.channeloutput = None
        self.decoded_list = None
        self.calculatedLikehood = np.full(
            (self.L, self.n,  int(np.log2(self.n))+1, 2), -1.0)

    def Decode(self, channeloutput):
        """
        受信系列をSCL復号するメソッド\n
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
        self.informationindex = self._GetInformationIndex()
        self.decoded_list = [np.array([], dtype=np.uint8)]

        for i in range(self.n):
            self._OneDecodingProcess(i)

    def _OneDecodingProcess(self, i):
        if i in self.informationindex:
            l = 0
            # tmp_calculatedLikehood = copy.deepcopy(self.calculatedLikehood)
            tmp_calculatedLikehood = self.calculatedLikehood  # 計算済みの尤度を一旦保持
            tmp_decoded_list = []  # 尤度と推定値を保持
            for lth_path in self.decoded_list:
                path_appended0 = np.append(lth_path, 0)
                path_appended1 = np.append(lth_path, 1)
                likehood_appended0 = self._CalculateLikelihood(
                    l, lth_path, i, tmp_calculatedLikehood[l], 0)
                likehood_appended1 = self._CalculateLikelihood(
                    l, lth_path, i, tmp_calculatedLikehood[l], 1)

                tmp_decoded_list.append(
                    [path_appended0, likehood_appended0, tmp_calculatedLikehood[l]])
                tmp_decoded_list.append(
                    [path_appended1, likehood_appended1, tmp_calculatedLikehood[l]])
                # ソートのため[パス、尤度、計算済み尤度]を要素とするリストを作る
                l += 1
            tmp_decoded_list = sorted(
                tmp_decoded_list, key=lambda x: x[1], reverse=True)

            if len(tmp_decoded_list) > self.L:
                tmp_decoded_list = tmp_decoded_list[:self.L]
            self.decoded_list = [x[0] for x in tmp_decoded_list]
            self.calculatedLikehood = np.array(
                [x[2] for x in tmp_decoded_list])

        else:
            l = 0
            for lth_path in self.decoded_list:
                lth_path = np.append(lth_path, 0)
                self.decoded_list[l] = lth_path
                l += 1

    def _SelectTrueMessage(self):
        """
        中間メッセージの復号完了後に、L個のリスト中から最も正しいと推定されるメッセージを求めるメソッド\n
        戻り値: 正しいと推定されるメッセージ
        """
        estimated_middlemessage = self.decoded_list[0]
        informationindex = self._GetInformationIndex()
        estimated_message = estimated_middlemessage[informationindex]
        return estimated_message

    def _CalculateLikelihood(self, l, lth_path, i, calculatedLikehood, u_i):
        """
        現在までの中間メッセージ推定値をもとに、次の値がu_iであるときの尤度を計算するメソッド\n
        l: リストのインデックス
        lth_path: l番目の現在までの中間メッセージ推定値のパス
        calculatedLikehood: 計算済みの尤度を格納してある配列
        i: 尤度を計算するインデックス
        u_i: i番目の値(int)
        """
        def W_awgn(n, chaneloutput, i, u_i, estimatedcodeword_u, calculatedLikehood, branch):
            """
            入力がu_iであるときの事後確率W(y^n,u^i-1|u_i)を計算する\n
            n: 符号長\n
            chaneloutpuy: 通信路出力\n
            i: 推定したいビットのインデックス\n
            u_i: 0か1
            estimatedcodeword_u: 現在までに推定された符号語ビット列
            calculatedLikehood: 計算済みの尤度を保持する N*logN*2 の行列
            branch: Tal,Vardyの論文中に出てくるブランチ
            """

            m = int(np.log2(n))
            if calculatedLikehood[i + n * branch][m][u_i] != -1.0:
                # 計算済みのW
                return calculatedLikehood[i + n * branch][m][u_i]

            if m == 0:
                # 再起の終了条件
                if u_i == 0:
                    W = norm.pdf(x=chaneloutput, loc=+1,
                                 scale=np.sqrt(self.N_0))
                else:
                    W = norm.pdf(x=chaneloutput, loc=-1,
                                 scale=np.sqrt(self.N_0))
                calculatedLikehood[i + n * branch][m][u_i] = W[0]*12
                return W[0]*12

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

        y = self.channeloutput
        n = self.n
        u = self.decoded_list[l]
        u_i = np.array([u_i], dtype=np.uint8)
        P = calculatedLikehood

        likehood = W_awgn(n, y, i, u_i, u, P, 0)
        return likehood

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
        return np.sort(informationindex[:self.k + self.r])


class CASCL_Decoder(SCL_Decoder):
    def __init__(self, k, n, L, r, snr, path):
        """
        受信系列を復号するクラス\n
        k: メッセージ長\n
        n: 符号長\n
        L: リストサイズ\n
        r: CRC長\n
        snr: ビットあたりのSN比（E_b/N_0)\n
        path: インデックスを相互情報量が小さい順に並べたファイルのパス
        """
        super().__init__(k, n, L, snr, path)
        self.r = r

    def _SelectTrueMessage(self):
        """
        中間メッセージの復号完了後に、L個のリスト中から最も正しいと推定されるメッセージを求めるメソッド\n
        戻り値: 正しいと推定されるメッセージ
        """
        informationindex = self._GetInformationIndex()
        # is_nocrc = True
        likelypath = self.decoded_list[0]

        for lth_path in self.decoded_list:
            message = lth_path[informationindex]
            crc_detector = CRC_Detector(message, self.r)
            if crc_detector.IsNoError():
                likelypath = lth_path
                break

        estimated_message = likelypath[informationindex]
        estimated_message = estimated_message[:self.k]
        return estimated_message


class multiCRC_SCL_Decoder(CASCL_Decoder):
    def __init__(self, k, n, L, r, threshold, snr, path):
        """
        受信系列を復号するクラス\n
        k: メッセージ長\n
        n: 符号長\n
        L: リストサイズ\n
        r: 総CRC長\n
        threshold: 各”メッセージ”サブブロックの終端インデックスのリスト\n
        snr: ビットあたりのSN比（E_b/N_0)\n
        path: インデックスを相互情報量が小さい順に並べたファイルのパス
        """
        super().__init__(k, n, L, r, snr, path)
        self.threshold = threshold

    def _DecodeMiddleMessage(self):
        """
        情報ビットと凍結ビットが含まれた中間メッセージをL個復号するメソッド\n
        """
        self.informationindex = self._GetInformationIndex()
        self.decoded_list = [np.array([], dtype=np.uint8)]

        for i in range(self.n):
            self._OneDecodingProcess(i)

            if i in self.informationindex[[x-1 for x in self.threshold]]:
                j = self.threshold[self.informationindex[[
                    x-1 for x in self.threshold]].tolist().index(i)]
                # print(j,self.k + self.r,"--")
                if j == (self.k + self.r)//2:
                    self._CheckSubblockCRC(0, j)
                elif j == self.k + self.r:
                    self._CheckSubblockCRC((self.k + self.r)//2, j)

    def _CheckSubblockCRC(self, startindex, endindex):
        """
        サブブロックでCRCをによるチェックを行い、CRCが通るものだけを新たなリストへと格納するメソッド\n
        starindex: メッセージサブブロックの開始インデックス\n
        endindex: メッセージサブブロックの終了インデックス\n
        """
        List_and_Likehood = [
            [self.decoded_list[x], self.calculatedLikehood[x]] for x in range(self.L)
        ]
        CRClen = self.r // len(self.threshold)
        # [パス, 計算済み尤度]というリストを要素に持つリストを作り、パス側でチェックを行う。

        collect_path = []
        for lal in List_and_Likehood:
            subblock = lal[0][self.informationindex[startindex:endindex]]
            crc_detector = CRC_Detector(subblock, CRClen)
            if crc_detector.IsNoError():
                collect_path.append(lal)

        if collect_path == []:
            pass
        else:
            self.decoded_list = [lal[0] for lal in List_and_Likehood]
            self.calculatedLikehood = [lal[1] for lal in List_and_Likehood]

    def _SelectTrueMessage(self):
        """
        中間メッセージの復号完了後に、L個のリスト中から最も正しいと推定されるメッセージを求めるメソッド\n
        戻り値: 正しいと推定されるメッセージ
        """
        estimated_message = self.decoded_list[0][self.informationindex]
        estimated_message = np.delete(estimated_message, np.s_[
                                      self.threshold[0]-self.r//2:self.threshold[0]], 0)
        estimated_message = np.delete(estimated_message, np.s_[self.k:], 0)

        return estimated_message


class SCL_Decoder_BSC:
    def __init__(self, k, n, L, p, path):
        """
        受信系列を復号するクラス\n
        k: メッセージ長\n
        n: 符号長\n
        p: 反転確率\n
        path: インデックスを相互情報量が小さい順に並べたファイルのパス
        """
        self.k = k
        self.n = n
        self.L = L
        self.r = 0
        self.p = p
        self.path = path

        self.channeloutput = None
        self.decoded_list = None
        self.calculatedLikehood = np.full(
            (self.L, self.n,  int(np.log2(self.n))+1, 2), -1.0)

    def Decode(self, channeloutput):
        """
        受信系列をSCL復号するメソッド\n
        channeloutput: AWGNチャネルからの受信系列
        """
        self.channeloutput = channeloutput

        self._DecodeMiddleMessage()
        decoded_message = self._GetMessage()
        return decoded_message

    def _DecodeMiddleMessage(self):
        """
        情報ビットと凍結ビットが含まれた中間メッセージをL個復号するメソッド\n
        """
        informationindex = self._GetInformationIndex()
        self.decoded_list = [np.array([], dtype=np.uint8)]

        for i in range(self.n):
            if i in informationindex:
                l = 0
                tmp_calculatedLikehood = copy.deepcopy(self.calculatedLikehood)
                tmp_decoded_list = []  # 尤度と推定値を保持
                for lth_path in self.decoded_list:
                    path_appended0 = np.append(lth_path, 0)
                    path_appended1 = np.append(lth_path, 1)
                    # print(tmp_calculatedLikehood[l], "\n-------------------------------")
                    likehood_appended0 = self._CalculateLikelihood(
                        l, lth_path, i, tmp_calculatedLikehood[l], 0)
                    # print(likehood_appended0)
                    # print(tmp_calculatedLikehood[l], "\n-------------------------------")
                    likehood_appended1 = self._CalculateLikelihood(
                        l, lth_path, i, tmp_calculatedLikehood[l], 1)
                    # print(likehood_appended1)
                    # print(tmp_calculatedLikehood[l], "\n-------------------------------")

                    # print(likehood_0appended)
                    # print(likehood_1appended)

                    tmp_decoded_list.append(
                        [path_appended0, likehood_appended0, tmp_calculatedLikehood[l]])
                    tmp_decoded_list.append(
                        [path_appended1, likehood_appended1, tmp_calculatedLikehood[l]])
                    l += 1
                tmp_decoded_list = sorted(
                    tmp_decoded_list, key=lambda x: x[1], reverse=True)

                if len(tmp_decoded_list) > self.L:
                    tmp_decoded_list = tmp_decoded_list[:self.L]
                self.decoded_list = [x[0] for x in tmp_decoded_list]
                self.calculatedLikehood = np.array(
                    [x[2] for x in tmp_decoded_list])

                # print(tmp_decoded_list[0][2])
                # print(self.calculatedLikehood)
                # print("-------------------------------------")

                # print([x[1] for x in tmp_decoded_list])
                # print("-------------------------------")
                # import time
                # time.sleep(0.1)

            else:
                l = 0
                for lth_path in self.decoded_list:
                    lth_path = np.append(lth_path, 0)
                    self.decoded_list[l] = lth_path
                    l += 1

    def _SelectTrueMessage(self):
        """
        中間メッセージの復号完了後に、L個のリスト中から最も正しいと推定されるメッセージを求めるメソッド\n
        戻り値: 正しいと推定されるメッセージ
        """
        estimated_middlemessage = self.decoded_list[0]
        informationindex = self._GetInformationIndex()
        estimated_message = estimated_middlemessage[informationindex]
        return estimated_message

    def _GetMessage(self):
        """
        情報ビットと凍結ビットが含まれた中間メッセージからメッセージを抜き出すメソッド
        """
        estimated_message = self._SelectTrueMessage()
        return estimated_message

    def _CalculateLikelihood(self, l, lth_path, i, calculatedLikehood, u_i):
        """
        現在までの中間メッセージ推定値をもとに、次の値がu_iであるときの尤度を計算するメソッド\n
        l: リストのインデックス
        lth_path: l番目の現在までの中間メッセージ推定値のパス
        calculatedLikehood: 計算済みの尤度を格納してある配列
        i: 尤度を計算するインデックス
        u_i: i番目の値(int)
        """
        def W_awgn(n, chaneloutput, i, u_i, estimatedcodeword_u, calculatedLikehood, branch):
            """
            入力がu_iであるときの事後確率W(y^n,u^i-1|u_i)を計算する\n
            n: 符号長\n
            chaneloutpuy: 通信路出力\n
            i: 推定したいビットのインデックス\n
            u_i: 0か1
            estimatedcodeword_u: 現在までに推定された符号語ビット列
            calculatedLikehood: 計算済みの尤度を保持する N*logN*2 の行列
            branch: Tal,Vardyの論文中に出てくるブランチ
            """

            m = int(np.log2(n))
            if calculatedLikehood[i + n * branch][m][u_i[0]] != -1.0:
                # 計算済みのW
                return calculatedLikehood[i + n * branch][m][u_i[0]]

            if m == 0:
                # 再起の終了条件
                if u_i == 0:
                    W = 1-self.p if chaneloutput == np.array([0]) else self.p
                else:
                    W = self.p if chaneloutput == np.array([0]) else 1-self.p
                calculatedLikehood[i + n * branch][m][u_i[0]] = W
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

        y = self.channeloutput
        n = self.n
        u = self.decoded_list[l]
        u_i = np.array([u_i], dtype=np.uint8)
        P = calculatedLikehood

        likehood = W_awgn(n, y, i, u_i, u, P, 0)
        return likehood

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
        return np.sort(informationindex[:self.k + self.r])


if __name__ == "__main__":

    y = [1.34514554, 0.51447536, -1.2354836, -0.33108537, 1.55344256, -1.16681963, -0.02234269, -2.02912666, -1.44900066, 1.08002942, 1.31746261, 1.26405955, -0.51584397, 0.62494649, 0.97840007, 0.9085162, 1.00229039, 0.97220703, 0.33728737, -1.37902176, 1.20984675, 0.83984627, 0.39712123, -1.06983388, 1.54179468, -0.14180542, 0.22666835, -1.93592488, -1.63751551, 1.64672191, -0.12620496, -1.21872203, -0.90345451, 2.08835325, -0.55024768, -1.68454128, 1.41258982, -1.30658192, 2.08097947, 1.50865343, 1.49549544, -1.16504868, -0.02524264, -1.96089825, 0.39502846, 1.60887821, -1.27000119, 0.44283835, -0.50880729, 1.72238738, 0.73123603, 0.21467353, 1.69062848, 0.97559634, -1.07133572, -0.44177208, -1.81305293, -1.38887069, -0.00603939, -1.76979874, 1.97228571, 0.2102428, -2.04842715, 0.79411394, -0.8515216, -1.13101104, -0.48945311, 1.17033106, 1.16381639, 1.34208949, -0.93210656, -0.76383703, 1.66052827, 0.65095328, 1.04023937, 0.40389697, -0.33430766, -1.17922471, 1.18598949, -1.13231611, 1.67923299, 2.22860324, 0.63082673, -1.01126508, 0.24491429, -1.20902261, 0.86837034, 0.02702819, 0.54482417, 0.288445, 0.84441515, -0.64317685, 1.97986793, 1.47340808, -2.18561526, -0.06392391, -0.71483422, -0.56922897, 1.21558369, -0.91918461, -1.56959494, 1.72771796, -0.06674475, 0.38688187, 0.91378982, 2.05472527, 1.64834937, -0.87908159, 1.25879512, 2.2470267, -0.94279808, 1.17362152, 2.63124353, -1.85565346, -0.4115832, -0.11921941, 3.34092654, -1.86961126, 1.27155006, 0.14757347, -0.51747161, -1.3141706, 0.03718765, -1.64460281, -1.43803264, 0.29138573, -1.23759369, -1.05239187,
         2.4035187, 0.19047854, -1.14861988, 0.67352387, -3.06221681, -0.61312623, 1.86236737, -0.64805296, 1.2216504, -0.23332585, -2.36029458, -2.26714724, 1.22812269, 0.21378886, -0.41752807, 2.1105814, -0.40902935, -0.28554437, -0.6558133, 1.49006954, -0.56030293, 2.0504912, 1.43055385, 0.77048595, -0.32424016, -1.73710745, -0.93647962, 0.54573996, -0.60089327, -0.96256648, 2.12138678, -1.10937376, -0.43094535, -0.53283646, 1.6293388, -1.56916045, 1.33944967, -1.25881347, -1.55135782, -0.11431616, 0.39360703, 1.21114677, -0.89520268, 1.02474696, 1.55595118, 0.85227623, -0.96508847, 0.14409127, -0.22871814, -1.43322785, -0.44593235, 1.75291771, 2.01268534, 0.71313445, -1.39045466, 0.93343789, -1.62398329, 0.78076024, 0.88065837, 0.39084331, 1.46742861, 1.17859794, 2.17364675, -0.33316382, -1.6261833, -0.51037034, 0.30616512, -0.77117375, -0.95659254, 1.81431459, 0.08262771, 1.75415599, 1.32160497, -1.18114502, 1.22956004, -0.50210675, 1.72726216, 0.81556826, 0.22276041, 0.08509882, -0.59841049, -1.41773575, -1.0648501, 1.70644713, -0.77569812, -2.45893281, 1.70995538, -0.63251334, 0.43130389, 2.05473657, -0.7306287, 1.00857848, 1.10788126, -1.35692408, 1.85633704, 0.47394836, -0.8731129, 1.28110216, 0.98670183, 1.78151045, 0.89262561, -0.73383537, -1.66682418, -1.28404702, 0.92680202, -1.98544018, 1.43508302, 2.32296812, 1.31830777, 0.74866523, 1.84977753, 0.09599822, -2.66720562, -0.83111353, -0.64250625, 0.19025406, 0.80968361, -0.37526651, -0.1781871, -1.29284996, 0.92116202, 0.03700649, 1.03085181, -0.20958776, 1.83345691, -1.29930251, -1.64256073, -1.71435009]
    # y = [1.0, 1.0, -1.0, 1.0, 1.0, -1.0, -1.0, -1.0, -1.0, 1.0, 1.0, 1.0, -1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, 1.0, 1.0, 1.0, -1.0, 1.0, 1.0, 1.0, -1.0, -1.0, 1.0, -1.0, -1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, -1.0, 1.0, 1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, -1.0, 1.0, 1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0, -1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, -1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, -1.0, -1.0, 1.0, -1.0, 1.0, -1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, -1.0, 1.0, 1.0, 1.0, -1.0, 1.0, -1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0, 1.0, -1.0, 1.0, 1.0, 1.0, -1.0, 1.0, 1.0, -1.0, -1.0, -1.0, 1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0, -1.0, 1.0, 1.0, -1.0, -1.0, -1.0, 1.0, -1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0]
    n = 256
    k = 128
    L = 4
    snr = 3
    i = 0
    u_i = 0
    u = np.array([], dtype=np.uint8)
    chaneltype = "AWGN"
    M = int(np.log2(n))
    R = k/n
    path = "./sort_I/"+chaneltype+"/sort_I_"+chaneltype + \
        "_"+str(M)+"_"+str(R)+"_"+str(snr)+"_.dat"

    d = SCL_Decoder(k, n, L, snr, path)
    msg = d.Decode(y)
    true = [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0,
            0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1]
    true = np.array(true, dtype=np.uint8)

    print(msg ^ true)
