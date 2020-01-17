import numpy as np
np.set_printoptions(linewidth=150)

def GetInformationIndex(K, path):
    informationindex = np.loadtxt(path, dtype=np.uint16)

    informationindex = np.flip(informationindex)
    return np.sort(informationindex[:K])

if __name__ == "__main__":
    infindex = GetInformationIndex(128+16, "./sort_I_8_0.06_20.dat")
    IW_n = np.loadtxt("IW.txt")

    #print(sum(IW_n[infindex[:threshold]]))
    #print(sum(IW_n[infindex[threshold:]]))
    unrel = np.where(IW_n[infindex]<0.9999)
    #print(IW_n[infindex[unrel]])
    print(unrel)
    print(unrel[0][55//2])