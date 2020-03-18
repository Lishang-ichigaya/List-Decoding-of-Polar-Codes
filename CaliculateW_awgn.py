import numpy as np
# from decimal import Decimal
from scipy.stats import norm 


# i +
#  n * branch,  m=log2(n)

def CaliculateW_awgn(variance, N, chaneloutput_y, i, u_i, estimatedcodeword_u, matrixP, branch):
    """
    入力がu_iであるときの事後確率W(y^n,u^i-1|u_i)を計算する
    N:符号長
    chaneloutpuy_y:通信路出力
    i:推定したいビット位置
    u_i: 0か1
    estimatedcodeword_u:現在までに推定された符号語ビット列
    matrixP: 事後確率を保持する N*logN*2 の行列
    """

    M = int(np.log2(N))
    if matrixP[i + N * branch][M][u_i[0]] != -1.0:
        # 計算済みのW
        return matrixP[i + N * branch][M][u_i[0]]

    if M == 0:
        # 再起の終了条件
        if u_i == 0:
            W = norm.pdf(x=chaneloutput_y, loc=+1, scale=np.sqrt(variance))
        else:
            W = norm.pdf(x=chaneloutput_y, loc=-1, scale=np.sqrt(variance))
        matrixP[i + N * branch][M][u_i[0]] = W
        return W

    # 以下再起的呼び出し
    y_1 = chaneloutput_y[:N//2]
    y_2 = chaneloutput_y[N//2:]

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
               * CaliculateW_awgn(variance, N//2, y_1, j//2, u_i ^ u_i_puls_1, hat_u1, matrixP, 2*branch)
               * CaliculateW_awgn(variance, N//2, y_2, j//2, u_i_puls_1, hat_u2, matrixP, 2*branch+1))
        u_i_puls_1 = np.array([1], dtype=np.uint8)
        W_2 = (0.5
               * CaliculateW_awgn(variance, N//2, y_1, j//2, u_i ^ u_i_puls_1, hat_u1, matrixP, 2*branch)
               * CaliculateW_awgn(variance, N//2, y_2, j//2, u_i_puls_1, hat_u2, matrixP, 2*branch+1))
        W = W_1 + W_2
    else:
        W = (0.5
             * CaliculateW_awgn(variance, N//2, y_1, j//2, hat_u_i_minus_1 ^ u_i, hat_u1, matrixP, 2*branch)
             * CaliculateW_awgn(variance, N//2, y_2, j//2, u_i, hat_u2, matrixP, 2*branch+1))
    matrixP[i + N * branch][M][u_i[0]] = W
    # print(W)
    return W

if __name__ == "__main__":
    p = 0.11
    # N = 4
    # chaneloutput = np.array([0, 0, 0, 0])
    # u_0toi = np.array([])

    # sum = 0
    # y_0to3 = [np.array([0, 0, 0, 0]), np.array([0, 0, 0, 1]), np.array([0, 0, 1, 0]), np.array([0, 0, 1, 1]),
    #           np.array([0, 1, 0, 0]), np.array([0, 1, 0, 1]), np.array([0, 1, 1, 0]), np.array([0, 1, 1, 1]),
    #           np.array([1, 0, 0, 0]), np.array([1, 0, 0, 1]), np.array([1, 0, 1, 0]), np.array([1, 0, 1, 1]),
    #           np.array([1, 1, 0, 0]), np.array([1, 1, 0, 1]), np.array([1, 1, 1, 0]), np.array([1, 1, 1, 1])]

    # i = 3
    # #all_u_0toi = [np.array([])]
    # #all_u_0toi = [np.array([0]), np.array([1])]
    # #all_u_0toi = [np.array([0,0]), np.array([1,0]),np.array([0,1]), np.array([1,1])]
    # all_u_0toi = [np.array([0, 0, 0]), np.array([1, 0, 0]), np.array([0, 1, 0]), np.array([1, 1, 0]),
    #               np.array([0, 0, 1]), np.array([1, 0, 1]), np.array([0, 1, 1]), np.array([1, 1, 1])]

    # for u_0toi in all_u_0toi:
    #     for chaneloutput in y_0to3:
    #         u_i = np.array([0])
    #         a = CalculateW_awgn_2(p, N, chaneloutput, i, np.array([0]), u_0toi)
    #         # print(a)
    #         a = float(a)
    #         u_i = np.array([1])
    #         b = CalculateW_awgn_2(p, N, chaneloutput, i, np.array([1]), u_0toi)
    #         # print(b)
    #         b = float(b)
    #         tmp1 = 0.5 * a * np.log2(a/(a+b))
    #         tmp2 = 0.5 * b * np.log2(b/(a+b))
    #         sum = sum + tmp1 + tmp2
    # print(i, ",", 1 + sum)
