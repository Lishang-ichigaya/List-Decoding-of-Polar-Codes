import numpy as np
from scipy.stats import norm
from tkinter import messagebox
import time
import sys
sys.path.append('C:\\Users\\pikac\\Documents\\MyPyLibrary')
import notification

def BinaryEntropy(p):
    return -p*np.log2(p)-(1-p)*np.log2(1-p)

if __name__ == "__main__":
    IW_n = np.loadtxt("aaa.text")
    for i in range(len(IW_n)):
        print(i, IW_n[i])