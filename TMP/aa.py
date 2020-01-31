import numpy as np
import sys
np.set_printoptions(linewidth=150)

def GetInformationIndex(K, path):
    informationindex = np.loadtxt(path, dtype=np.uint16)

    informationindex = np.flip(informationindex)
    return np.sort(informationindex[:K])

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("aa.py m P r k\nm:符号長のlog2 P:反転確率 r:CRC長 k:メッセージ長")
        exit()

    m = int(sys.argv[1])
    P = float(sys.argv[2])
    r = int(sys.argv[3])
    k = int(sys.argv[4])
    infindex = GetInformationIndex(k+r, "../sort_I/sort_I_"+str(m)+"_"+str(P)+"_20.dat")
    IW_n = np.loadtxt(str(2**m)+"_IW"+sys.argv[2][1:]+".txt")

    #print(sum(IW_n[infindex[:threshold]]))
    #print(sum(IW_n[infindex[threshold:]]))
    unrel = np.where(IW_n[infindex]<0.993)
    #print(IW_n[infindex[unrel]])
    #print(unrel)
    print(unrel[0][len(unrel[0])//2]+1)