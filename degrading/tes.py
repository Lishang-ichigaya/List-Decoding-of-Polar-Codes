import numpy as np
from scipy.stats import norm
from tkinter import messagebox
import time
import notification

def BinaryEntropy(p):
    return -p*np.log2(p)-(1-p)*np.log2(1-p)

if __name__ == "__main__":
    # time.sleep(1)
    # messagebox.showinfo("end","おわり")
    notification.Notice()