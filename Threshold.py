import numpy as np


def GetInformationIndex(k, n):
    """
    情報ビットに対応するインデックス集合（情報インデックス）を得るメソッド
    戻り値: 情報インデックス
    """
    path = "./sort_I/AWGN/sort_I_AWGN_" + \
        str(int(np.log2(n)))+"_"+str(0.5)+"_"+"1"+"_.dat"
    informationindex = np.loadtxt(path, dtype=np.uint16)
    informationindex = np.flip(informationindex)
    return np.sort(informationindex[:k])


if __name__ == "__main__":
    k = 512 + 16
    n = 1024
    snr = 1
    IW_n = np.loadtxt("./IW/IW_{}_{}.txt".format(n, snr))
    division_num = 4
    IW_threshold = 0.99
    information_index = GetInformationIndex(k, n)

    # print(IW_n[information_index]) # 情報ビットの相互情報量
    unreliable_message_index = np.where(
        IW_n[information_index] < IW_threshold)  # 信頼性が低いメッセージのインデックス
    # print(unreliable_message_index[0])

    # 信頼性が低いビットの相互情報量
    unreliable_bitchannel_index = information_index[unreliable_message_index[0]]
    # print("信頼性の低いビット\n", unreliable_bitchannel_index) #信頼性が低いビットのインデックス

    threshold_message = unreliable_message_index[0][[
        x*len(unreliable_bitchannel_index)//division_num - 1 for x in range(1, division_num)]]
    threshold_bitchannel = unreliable_bitchannel_index[[
        x*len(unreliable_bitchannel_index)//division_num - 1 for x in range(1, division_num)]]
    print("メッセージのスレッショルド:\t", threshold_message)
    print("ビットチャネルのスレッショルド:\t", threshold_bitchannel)

    print("\n従来メッセージのスレッショルド: \t", [
          i*k//division_num - 1 for i in range(1, division_num)])
    print("従来ビットチャネルのスレッショルド:\t", information_index[[
          i*k//division_num - 1 for i in range(1, division_num)]])
