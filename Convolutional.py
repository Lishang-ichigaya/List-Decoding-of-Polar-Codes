import numpy as np


class ConvolutionalCodeEncoder:
    def __init__(self, c=np.array([1, 1, 1], dtype=np.uint8)):
        """
        レート1の畳み込み符号（変換）のクラス\n
        c: 畳み込みのインパルス応答\n
        """
        self.c = c

    def Encode(self, message):
        """
        畳み込み符号（変換）を行うメソッド\n
        message: 変換したいメッセージ\n
        """
        k = np.size(message)
        c = self.c
        len_c = np.size(c)
        message = np.concatenate([np.zeros(len_c-1, dtype=np.uint8), message])
        # print(message)
        codeword = np.zeros(k, dtype=np.uint8)

        for i in range(len_c-1, k+len_c-1):
            # print(i)
            # u = [ c[j]*message[i-j] for j in range(np.size(c)) ]
            u = []
            for j in range(len_c):
                # print(j, i-j)
                u.append(c[j]*message[i-j])
            # print(u)
            codeword[i-len_c+1] = sum(u) % 2
            # print(i-len_c+1)
        
        return codeword

if __name__ == "__main__":
    ce = ConvolutionalCodeEncoder(np.array([1,1,1], dtype=np.uint8))
    message = np.array([1, 0, 0, 0, 1, 1, 0, 1, 0, 1])
    print(message)
    cw = ce.Encode(message)
    print(cw)
