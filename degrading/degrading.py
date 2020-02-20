import numpy as np
from CaliculateW import CalculateW_BSC_2
from BMSchannel import BMSchannel

def degrading_merge():
    return 0



if __name__ == "__main__":
    N=2
    i=0
    p = 0.1
    W_0 = np.array([[1-p, p],[p, 1-p]])
    W_1_0 = np.zeros([2,4])
    W_1_1 = np.zeros([2,8])
    for u in [0,1]:
        k=0
        for y in [[0,0],[0,1],[1,0],[1,1]]:
            W_1_0[u][k] = CalculateW_BSC_2(p, N, y, i, u, np.array([]))
            k+=1
    print(W_1_0)

    # i=1
    # for u_i in [0,1]:
    #     k=0
    #     for u in [0,1]:
    #         for y in [[0,0],[0,1],[1,0],[1,1]]:
    #             W_1_1[u_i][k] = CalculateW_BSC_2(p, N, y, i, u_i, np.array([u]))
    #             print(k,y,u,u_i)
    #             print(W_1_1[u][k])
    #             k+=1
    # print(W_1_1)

