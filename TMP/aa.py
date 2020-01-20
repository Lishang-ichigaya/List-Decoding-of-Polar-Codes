import numpy as np
import sys
np.set_printoptions(linewidth=150)

def GetInformationIndex(K, path):
    informationindex = np.loadtxt(path, dtype=np.uint16)

    informationindex = np.flip(informationindex)
    return np.sort(informationindex[:K])

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("aa.py P r\nP:反転確率 r:CRC長")
        exit

    P = float(sys.argv[1])
    r = int(sys.argv[2])
    infindex = GetInformationIndex(128+r, "./sort_I_8_"+str(P)+"_20.dat")
    IW_n = np.loadtxt("IW.txt")

    #print(sum(IW_n[infindex[:threshold]]))
    #print(sum(IW_n[infindex[threshold:]]))
    unrel = np.where(IW_n[infindex]<0.9999)
    #print(IW_n[infindex[unrel]])
    #print(unrel)
    print(unrel[0][len(unrel[0])//2])