import numpy as np
import time

class Encoder:
    def __init__(self, K, N, message, path, checker=True):
        """
        エンコーダクラスの初期化
        K:メッセージ長
        N:符号長
        message: 0,1のメッセージ
        path: 相互情報量の小さい順にインデックスを並べたファイルのパス
        checker: メッセージもどきを表示するか否か
        """
        self.K = K
        self.message = message
        self.N = N
        self.message_prime = np.zeros(N, dtype=np.uint8)
        self.codeword = np.zeros(N, dtype=np.uint8)
        self.path = path
        self.checker = checker

    def MakeCodeworde(self):
        informationindex = GetInformationIndex(self.K, self.path)
        self.message_prime = np.zeros([self.N], dtype=np.uint8)
        self.message_prime[informationindex] = self.message
        if self.checker == True:
            print("メッセージもどき： \t", self.message_prime)
        #↓の処理がそこそこ重いけど、numpyだしもう高速化はむり？
        self.codeword = np.dot(self.message_prime, GetGeneratorMatrix(self.N)) % 2
        self.codeword = self.codeword.A1
    def GetMessagePrime(self):
        return self.message_prime


class InterleavedEncoder(Encoder):
    def __init__(self, k, N, r, message, parity, path, checker=True):
        super().__init__(k, N, message, path, checker)
        #self.K = k + r
        #self.message = np.concatenate([message, parity])
        self.r = r              #CRC等の長さ
        self.parity = parity    #誤り検出や訂正を行うビット

    def MakeCodeworde(self):
        informationindex = GetInformationIndex(self.K, self.path)
        paritybitindex = GetParitybitIndex(self.K, self.r, self.path)
        self.message_prime = np.zeros([self.N], dtype=np.uint8)
        self.message_prime[informationindex] = self.message
        self.message_prime[paritybitindex] = self.parity
        if self.checker == True:
            print("メッセージもどき： \t", self.message_prime)
        self.codeword = np.dot(self.message_prime, GetGeneratorMatrix(self.N)) % 2
        self.codeword = self.codeword.A1

def GetGeneratorMatrix(N):
    """
    ポーラ符号の生成行列を作成
    M: 符号長N
    """
    M = int(np.log2(N))

    matrixF = np.array([[1, 0], [1, 1]], dtype=np.uint8)

    matrixG = matrixF
    for i in range(1, M):
        tmp = matrixG
        matrixG = np.dot(
            GetPermutationMatrix(i+1),
            np.kron(matrixF, tmp)
        )
    return matrixG

def GetPermutationMatrix(M):
    """
    偶数番目を前に、奇数番目を後ろに置き換える行列を得る
    M: 符号長Nについて、N=2^Mを満たすM

    例:
    [1,0,0,0]  [1,0,0,0]
    [0,1,0,0]->[0,0,1,0]
    [0,0,1,0]  [0,1,0,0]
    [0,0,0,1]  [0,0,0,1]
    """
    if M == 1:
        return np.identity(1, dtype=np.uint8)
    matrixI_2 = np.matrix([[1, 0], [0, 1]])
    matrixR = np.matrix([[1, 0], [0, 1]])
    for i in range(M-1):
        matrixR = np.kron(matrixI_2, matrixR)
    matrixEven, matrixOdd = matrixR[::2], matrixR[1::2]
    matrixR = np.concatenate([matrixEven, matrixOdd]).T
    return matrixR

def GetInformationIndex(K, path):
    """
    情報ビットに対応するインデックス集合を得る
    K:メッセージの長さ
    """
    informationindex = np.loadtxt(path, dtype=np.uint16)
    #print(informationindex)
    # N = 65536 までは耐えられるようにunit16を使う
    # unit8 だとN=256までしか使えない
    informationindex = np.flip(informationindex)
    # 相互情報量の小さい順に、インデックスを並べ替えたものを外部で用意しておく
    return np.sort(informationindex[:K])

def GetParitybitIndex(K, r, path):
    """
    信頼性が比較的低いインデックス集合を得る。パリティビットに使用するかも
    K:メッセージの長さ
    r:パリティビットの長さ
    """
    paritybitindex = np.loadtxt(path, dtype=np.uint16)
    paritybitindex = np.flip(paritybitindex)
    return np.sort(paritybitindex[K:K+r])

if __name__ == "__main__":
    K = 4
    N = 8
    #path = "./sort_I/sort_I_2_0.11_20.dat"
    path = "./sort_I/sortI_BEC_0.5_8.dat"
    message = np.array([1, 1, 1, 1])
    encoder0 = Encoder(K, N, message, path)
    encoder0.MakeCodeworde()

    print(encoder0.message)
    print(GetGeneratorMatrix(N))
    print(encoder0.codeword)
