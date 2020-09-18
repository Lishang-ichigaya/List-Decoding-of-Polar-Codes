import numpy as np


class CRC:
    def __init__(self, message, CRClen):
        if CRClen == 1:
            self.GeneratorPolynomial = np.array([1, 1], dtype=np.uint8)
        elif CRClen == 2:
            self.GeneratorPolynomial = np.array([1, 0 ,1], dtype=np.uint8)
        elif CRClen == 3:
            self.GeneratorPolynomial = np.array([1, 0, 1, 1], dtype=np.uint8)
        elif CRClen == 4:
            self.GeneratorPolynomial = np.array([1, 0, 0, 1, 1], dtype=np.uint8)
        elif CRClen == 5:
            self.GeneratorPolynomial = np.array([1, 1, 0, 1, 0, 1], dtype=np.uint8)
        elif CRClen == 6:
            self.GeneratorPolynomial = np.array([1, 0, 0, 0, 0, 1, 1], dtype=np.uint8)
        elif CRClen == 8:
            self.GeneratorPolynomial = np.array([1, 1, 1, 0, 1, 0, 1, 0, 1], dtype=np.uint8)
        elif CRClen == 12:
            self.GeneratorPolynomial = np.array([1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1], dtype=np.uint8)
        elif CRClen == 16:
            self.GeneratorPolynomial = np.array([1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1], dtype=np.uint8)
        else:
            raise ValueError("適切なCRC長の使用")
        self.Message = message
        self.CRC = np.array([], dtype=np.uint8)
        self.K = np.size(self.Message)
        self.r = np.size(self.GeneratorPolynomial)


class CRC_Encoder(CRC):
    def __init__(self, message, CRClen=4):
        """
        CRCの符号器を初期化
        message: 送信メッセージ
        CRClen=4: CRCの長さ。2,3,4,6,8,16以外の場合は1bitCRC(パリティビット)になる
        """
        super().__init__(message, CRClen)
        self.codeword = np.array([], dtype=np.uint8)

    def MakeCRC(self):
        tmp_GenPolynomial = np.concatenate([self.GeneratorPolynomial, np.zeros(self.K-1, dtype=np.uint8)])
        tmp_CRC = np.concatenate([self.Message, np.zeros(self.r-1, dtype=np.uint8)])
        for i in range(self.K):
            # print(tmp_CRC)
            # print(tmp_GenPolynomial)
            if tmp_CRC[i] == 1:
                tmp_CRC = tmp_CRC ^ tmp_GenPolynomial
            tmp_GenPolynomial = np.roll(tmp_GenPolynomial, 1)
        # print(tmp_CRC)
        self.CRC = tmp_CRC[self.K:]
        # print(self.CRC)

    def Encode(self):
        self.MakeCRC()
        self.codeword = np.concatenate([self.Message, self.CRC])
        return self.codeword


class CRC_Detector(CRC):
    def __init__(self, chaneloutput, CRClen=4):
        """
        CRCの検出器を初期化。
        chaneloutput: 通信路出力
        CRClen=4: CRCの長さ。2,4,8,16以外の場合は1bitCRC(パリティビット)になる
        """
        super().__init__(np.array([], dtype=np.uint8), CRClen)
        self.chaneloutput = chaneloutput
        self.K = np.size(chaneloutput) - self.r + 1
        self.remainder = np.array([], dtype=np.uint8)
        self.decector = False

    def IsNoError(self):
        """
        CRCの計算を行い誤りが存在するか否かを返すメソッド。
        誤り無し：True，誤り有り：False を返す。
        """
        self.Detecte()
        return self.decector

    def Detecte(self):
        tmp_remainder = self.chaneloutput
        tmp_GenPolynomial = np.concatenate([self.GeneratorPolynomial, np.zeros(self.K - 1, dtype=np.uint8)])
        # print(tmp_remainder)
        # print(tmp_GenPolynomial)
        for i in range(self.K + self.r - 1):
            # print(tmp_GenPolynomial)
            if tmp_remainder[i] == 1:
                tmp_remainder = tmp_remainder ^ tmp_GenPolynomial
            tmp_GenPolynomial = np.roll(tmp_GenPolynomial, 1)
            # print(tmp_remainder)
        self.remainder = tmp_remainder
        # print(self.remainder)
        if np.count_nonzero(self.remainder) == 0:
            self.decector = True
        else:
            self.decector = False

    def GetMessage(self):
        return self.chaneloutput[:self.K]
