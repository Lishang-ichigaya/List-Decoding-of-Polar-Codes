import numpy as np
from Convolutional import ConvolutionalCodeEncoder
from Encoder import Encoder


class PAC_Encoder(Encoder):
    def __init__(self, k, n, c, path):
        """
        メッセージをPAC符号で符号化するクラス\n
        k: メッセージ長\n
        n: 符号長\n
        c: 畳み込みのインパルス応答\n
        path: 情報ビットを昇順に並べたファイルのパス
        """
        self.k = k
        self.n = n
        self.c = c
        self.path = path

    def Encode(self, message):
        """
        メッセージを符号化するメソッド\n
        message: 符号化したいメッセージ\n
        戻り値: 符号語
        """
        informationindex = self._GetInformationIndex()
        rate_profiled_message = np.zeros([self.n], dtype=np.uint8)
        rate_profiled_message[informationindex] = message
        # print(rate_profiled_message)
        conv_enc = ConvolutionalCodeEncoder(self.c)
        convoluved_message = conv_enc.Encode(rate_profiled_message)
        # print(convoluved_message)

        polar_codeword = np.dot(
            convoluved_message, self._GetGeneratorMatrix()) % 2
        return polar_codeword


if __name__ == "__main__":
    k = 4
    n = 8
    m = int(np.log2(n))
    R = k/n
    pe = PAC_Encoder(k, n, np.array([1, 1, 1], dtype=np.uint8),
                     "./sort_I/AWGN/sort_I_AWGN_"+str(m)+"_"+str(R)+"_"+"1"+"_.dat")
    message = np.array([1, 1, 1, 1], dtype=np.uint8)
    cw = pe.Encode(message)
    print(cw)

