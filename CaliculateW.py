import numpy as np
from decimal import Decimal

# i +
#  n * branch,  m=log2(n)


def CalculateW_BSC(p, N, chaneloutput_y, i, u_i, estimatedcodeword_u, matrixP, branch):
    """
    入力がu_iであるときの事後確率W(y^n,u^i-1|u_i)を計算する
    N:符号長
    chaneloutpuy_y:受信したビット列
    i:推定したいビット位置
    u_i: 0か1
    estimatedcodeword_u:現在までに推定された符号語ビット列
    matrixP: 事後確率を保持する N*logN*2 の行列
    """

    M = int(np.log2(N))
    if matrixP[i + N * branch][M][u_i[0]] != Decimal("-1"):
        # 計算済みのW
        return matrixP[i + N * branch][M][u_i[0]]

    if M == 0:
        # 再起の終了条件
        if u_i == np.array([0]):
            W = Decimal(1-p) if chaneloutput_y == np.array([0]) else Decimal(p)
        elif u_i == np.array([1]):
            W = Decimal(p) if chaneloutput_y == np.array([0]) else Decimal(1-p)
        else:
            print("error")
            exit(1)  # 起こったらだめ
        matrixP[i + N * branch][M][u_i[0]] = W
        return W

    # 以下再起的呼び出し
    y_1 = chaneloutput_y[:int(N/2)]
    y_2 = chaneloutput_y[int(N/2):]

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
        #u_i+1が0と1の場合について和をとる
        u_i_puls_1 = np.array([0], dtype=np.uint8)
        W_1 = (Decimal(1/2) 
            * CalculateW_BSC(p, int(N/2), y_1, int(j/2), u_i ^ u_i_puls_1, hat_u1, matrixP,2*branch)
            * CalculateW_BSC(p, int(N/2), y_2, int(j/2), u_i_puls_1, hat_u2, matrixP, 2*branch+1))
        u_i_puls_1 = np.array([1], dtype=np.uint8)
        W_2 = (Decimal(1/2) 
            * CalculateW_BSC(p, int(N/2), y_1, int(j/2), u_i ^ u_i_puls_1, hat_u1, matrixP,2*branch)
            * CalculateW_BSC(p, int(N/2), y_2, int(j/2), u_i_puls_1, hat_u2, matrixP, 2*branch+1))
        W = W_1 + W_2
    else:
        W = (Decimal(1/2) 
            * CalculateW_BSC(p, int(N/2), y_1, int(j/2), hat_u_i_minus_1 ^ u_i, hat_u1, matrixP,2*branch)
            * CalculateW_BSC(p, int(N/2), y_2, int(j/2), u_i, hat_u2, matrixP, 2*branch+1))
    matrixP[i + N * branch][M][u_i[0]] = W
    return W


def CalculateLR_BEC(e, N, chaneloutput_y, i, estimatedcodeword_u, LRmatrix, branch):
    """
    尤度比LRを計算する
    N:符号長
    chaneloutpuy_y:受信したビット列
    i:推定したいビット位置
    estimatedcodeword_u:現在までに推定された符号語ビット列
    """

    M = int(np.log2(N))
    if LRmatrix[i + N * branch][M] != Decimal("-1"):
        #計算済みのLR(i, n, branch)
        return LRmatrix[i + N * branch][M]

    if N == 1:
        if chaneloutput_y == np.array([0]):
            LR_tmp = Decimal('10000')  # 正しくは無限大
        elif chaneloutput_y == np.array([1]):
            LR_tmp = Decimal('0.00001')
        elif chaneloutput_y == np.array([3]):
            LR_tmp = Decimal('1')
        else:
            # ありえないのでエラー
            exit(1)
        LRmatrix[i + N * branch][M] = LR_tmp
        return LRmatrix[i + N * branch][M]

    y_1 = chaneloutput_y[:int(N/2)]
    y_2 = chaneloutput_y[int(N/2):]

    if i > 1:
        # ここからuが存在するとき
        hat_u_i = estimatedcodeword_u[i-1]

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
            hat_u_i = estimatedcodeword_u[0]

        j = 0
        hat_u1 = np.array([], dtype=np.uint8)
        hat_u2 = np.array([], dtype=np.uint8)

    # Arikanが提案した再起式に従って、再帰的に計算。
    if i % 2 == 0:
        LR1 = CalculateLR_BEC(e, int(N/2), y_1, int(j/2),
                              hat_u1, LRmatrix, 2*branch)
        LR2 = CalculateLR_BEC(e, int(N/2), y_2, int(j/2),
                              hat_u2, LRmatrix, 2*branch+1)
        LR = (
            (LR1 * LR2 + 1)
            /
            (LR1 + LR2)
        )
    else:
        LR1 = CalculateLR_BEC(e, int(N/2), y_1, int(j/2),
                              hat_u1, LRmatrix, 2*branch)
        LR2 = CalculateLR_BEC(e, int(N/2), y_2, int(j/2),
                              hat_u2, LRmatrix, 2*branch+1)
        if hat_u_i == 0:
            LR = LR1 * LR2
        else:
            LR = np.reciprocal(LR1) * LR2
    LRmatrix[i + N * branch][M] = LR
    return LR


if __name__ == "__main__":
    P = 0.1
    N = 2
    matrixP = np.full((N,  int(np.log2(N))+1, 2), Decimal("-1"))
    u_i = np.array([0])
    a = CalculateW_BSC(P, N, np.array([1,0]), 1, u_i, np.array([1]), matrixP, 0)
    print(a)
