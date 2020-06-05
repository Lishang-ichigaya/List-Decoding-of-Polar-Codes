import numpy as np

def GetInformationIndex(k, n):
    """
    情報ビットに対応するインデックス集合（情報インデックス）を得るメソッド
    戻り値: 情報インデックス
    """
    path =  "./sort_I/AWGN/sort_I_AWGN_"+str(int(np.log2(n)))+"_"+str(k/n)+"_"+"1"+"_.dat"
    informationindex = np.loadtxt(path, dtype=np.uint16)
    informationindex = np.flip(informationindex)
    return np.sort(informationindex[:k])

if __name__ == "__main__":
    k = 128
    n = 256
    snr = 1
    IW_n = np.loadtxt("./IW/IW_{}_{}.txt".format(n,snr))
    division_num = 2
    IW_threshold = 0.99

    information_index = GetInformationIndex(k, n)
    # print(IW_n[information_index]) # 情報ビットの相互情報量
    unreliable_bit = np.where(IW_n[information_index] < IW_threshold)
    # print(IW_n[information_index[unreliable_bit[0]]]) # 信頼性が低いビットの相互情報量
    unreliable_bitindex = information_index[unreliable_bit[0]]
    # print(unreliable_bitindex) #信頼性が低いビットのインデックス
    threshold = unreliable_bitindex[ [x*len(unreliable_bitindex)//division_num - 1 for x in range(1,division_num+1)]]
    print("スレッショルド: ",threshold)