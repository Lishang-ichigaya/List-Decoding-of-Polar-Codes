import numpy as np
from decimal import Decimal
from decimal import getcontext
# i + n * branch,  m=log2(n)


def CalculateLR_BSC(p, N, chaneloutput_y, i, estimatedcodeword_u, LRmatrix, branch):
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
        LR_1 = Decimal(str(p/(1-p))) if chaneloutput_y == np.array([1]) else Decimal(str((1-p)/p))
        LRmatrix[i + N * branch][M] = LR_1
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
        LR1 = CalculateLR_BSC(p, int(N/2), y_1, int(j/2),
                          hat_u1, LRmatrix, 2*branch)
        LR2 = CalculateLR_BSC(p, int(N/2), y_2, int(j/2),
                          hat_u2, LRmatrix, 2*branch+1)
        LR = (
            (LR1 * LR2 + 1)
            /
            (LR1 + LR2)
        )
    else:
        LR1 = CalculateLR_BSC(p, int(N/2), y_1, int(j/2),
                          hat_u1, LRmatrix, 2*branch)
        LR2 = CalculateLR_BSC(p, int(N/2), y_2, int(j/2),
                          hat_u2, LRmatrix, 2*branch+1)
        if hat_u_i == 0:
            LR = LR1 * LR2
        else:
            LR = np.reciprocal(LR1) * LR2
    LRmatrix[i + N * branch][M] = LR
    #print(i, M, '{:.30f}'.format(LR))
    return LR

def CalculateLR_BSC_2(p, N, chaneloutput_y, i, estimatedcodeword_u):
    """
    尤度比LRを計算する
    N:符号長
    chaneloutpuy_y:受信したビット列
    i:推定したいビット位置
    estimatedcodeword_u:現在までに推定された符号語ビット列
    """

    M = int(np.log2(N))
    if N == 1:
        LR_1 = Decimal(str(p/(1-p))) if chaneloutput_y == np.array([1]) else Decimal(str((1-p)/p))
        return LR_1

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
        LR1 = CalculateLR_BSC_2(p, int(N/2), y_1, int(j/2),
                          hat_u1)
        LR2 = CalculateLR_BSC_2(p, int(N/2), y_2, int(j/2),
                          hat_u2)
        LR = (
            (LR1 * LR2 + 1)
            /
            (LR1 + LR2)
        )
    else:
        LR1 = CalculateLR_BSC_2(p, int(N/2), y_1, int(j/2),
                          hat_u1)
        LR2 = CalculateLR_BSC_2(p, int(N/2), y_2, int(j/2),
                          hat_u2)
        if hat_u_i == 0:
            LR = LR1 * LR2
        else:
            LR = np.reciprocal(LR1) * LR2
    #print(i, M, '{:.30f}'.format(LR))
    return LR


def CalculateLR_BEC(e, N, chaneloutput_y, i, estimatedcodeword_u, LRmatrix, branch):
    """
    尤度比LRを計算する
    N:符号長
    chaneloutpuy_y:受信したビット列
    i:推定したいビット位置
    estimatedcodeword_u:現在までに推定された符号語ビット列
    """
    M = int(np.log2(N))
    #print(M ,branch)
    if LRmatrix[i + N * branch][M] != Decimal("-1"):
        #計算済みのLR(i, n, branch)
        return LRmatrix[i + N * branch][M]

    if N == 1:
        if chaneloutput_y == np.array([0]):
            LR_tmp = Decimal('1000000000')#正しくは無限大
        elif chaneloutput_y == np.array([1]):
            LR_tmp = Decimal('0.00000001')
        elif chaneloutput_y == np.array([3]):
            LR_tmp = Decimal('1')
        else:
            #ありえないのでエラー
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

def CalculateLR_BEC_2(e, N, chaneloutput_y, i, estimatedcodeword_u):
    """
    尤度比LRを計算する
    N:符号長
    chaneloutpuy_y:受信したビット列
    i:推定したいビット位置
    estimatedcodeword_u:現在までに推定された符号語ビット列
    """

    M = int(np.log2(N))
    if N == 1:
        if chaneloutput_y == np.array([0]):
            LR_tmp = Decimal('10000') #正しくは無限大
        elif chaneloutput_y == np.array([1]):
            LR_tmp = Decimal('0.00001')
        elif chaneloutput_y == np.array([3]):
            LR_tmp = Decimal('1')
        else:
            #ありえないのでエラー
            exit(1)
        return  LR_tmp

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
        LR1 = CalculateLR_BEC_2(e, int(N/2), y_1, int(j/2),
                          hat_u1)
        LR2 = CalculateLR_BEC_2(e, int(N/2), y_2, int(j/2),
                          hat_u2)
        LR = (
            (LR1 * LR2 + 1)
            /
            (LR1 + LR2)
        )
    else:
        LR1 = CalculateLR_BEC_2(e, int(N/2), y_1, int(j/2),
                          hat_u1)
        LR2 = CalculateLR_BEC_2(e, int(N/2), y_2, int(j/2),
                          hat_u2)
        if hat_u_i == 0:
            LR = LR1 * LR2
        else:
            LR = np.reciprocal(LR1) * LR2
    return LR

if __name__ == "__main__":
    P = 0.06
    N = 32
    chaneloutput = np.array([1,0,1,0,1,0,0,1,1,1,1,0,0,0,1,0,0,0,1,1,1,1,1,0,1,1,0,1,1,1,1,1])
    u_0toi = np.array([0,0,0,0,0,0,0,1,0,0,0,0,0,0])
    i = 13
    u_i = np.array([0])
    a = CalculateLR_BSC_2(P, N, chaneloutput, i, u_0toi)
    print(a)