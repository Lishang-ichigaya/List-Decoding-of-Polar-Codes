from subprocess import check_call
import numpy as np
import sys
import time
from tkinter import messagebox

from message import Message
#from codeword import CodeWorde
from Encoder import Encoder
from chanel import BSC
from Decoder import DecoderW
from Decoder import DecoderLR
from Decoder import ListDecoder

if __name__ == '__main__':
    K = 64
    N = 128
    L = 4
    M = int(np.log2(N))
    chaneltype = "BSC"
    P = 0.11
    path = "./sort_I/sort_I_" + str(M) + "_" + str(P) + "_" + "20" + ".dat"
    # path ="./polarcode/"+"sort_I_" + str(M) + "_" + str(P) + "_" + "20" + ".dat"

    kaisu = 10
    if len(sys.argv) == 2:
        # 相互情報量を計算する場合は 'c' オプションをつける
        if sys.argv[1] == "c":
            check_call(["./sort_I/calIdmcDp.exe", str(M), str(P), "20"])

        if sys.argv[1] == "ber":
            kaisu = 1000

            for j in range(1):
                eroorcount0 = 0
                frameerrorcout0 = 0
                eroorcount1 = 0
                frameerrorcout1 = 0
                #K *= 2
                #N *= 2
                path = path = "./sort_I/sort_I_" + str(int(np.log2(N))) + "_" + str(P) + "_" + "20" + ".dat"
                start = time.time()
                for i in range(kaisu):
                    message = Message(K)
                    message.MakeMessage()

                    encoder0 = Encoder(K, N, message.message, path, False)
                    encoder0.MakeCodeworde()
                    
                    bsc = BSC(P)
                    bsc.input = encoder0.codeword
                    bsc.Transmission()
                    output = bsc.output
                
                    decoder0 = DecoderW(K, N ,output, chaneltype, path, False)
                    decoder0.DecodeMessage(P)
                    hat_message0 = Message(K)
                    hat_message0.message = decoder0.hat_message

                    decoder1 = DecoderLR(K, N ,output, chaneltype, path, False)
                    decoder1.DecodeMessage(P)
                    hat_message1 = Message(K)
                    hat_message1.message = decoder1.hat_message

                    error0 = np.bitwise_xor(message.message, hat_message0.message)
                    error1 = np.bitwise_xor(message.message, hat_message0.message)

                    eroorcount0 += np.count_nonzero(error0)
                    eroorcount1 += np.count_nonzero(error1)

                    frameerrorcout0 += 0 if np.count_nonzero(error0) == 0 else 1
                    frameerrorcout1 += 0 if np.count_nonzero(error1) == 0 else 1
                    print(i, "/", kaisu, "回目, ",
                        0 if np.count_nonzero(error0) == 0 else 1,
                        0 if np.count_nonzero(error1) == 0 else 1)
                end = time.time()

                with open("Kekka1_bsc.txt",mode='a') as f:
                    f.write("K="+str(K)+", N="+str(N)+"\n")
                    f.write("送信: "+ str(K*kaisu)+ ", W復号誤り: "+ str(eroorcount0)+", LR復号誤り: "+ str(eroorcount1)+"\n")
                    f.write("FER__W: "+ str(frameerrorcout0/kaisu)+"\n")
                    f.write("FER_LR: "+ str(frameerrorcout1/kaisu)+"\n")
                    f.write("BER__W: "+ str(eroorcount0/(K*kaisu))+"\n")
                    f.write("BER_LR: "+ str(eroorcount1/(K*kaisu))+"\n")
                    f.write("実行時間: "+ str(end-start)+"\n")

    if len(sys.argv) == 1:
        print("K=", K, "N=", N, "L=",L)

        message = Message(K)
        message.MakeMessage()
        print("メッセージ:\t\t", message.message)

        encoder0 = Encoder(K, N, message.message, path)
        encoder0.MakeCodeworde()
        print("符号語:\t\t\t", encoder0.codeword)

        bsc = BSC(P)
        bsc.input = encoder0.codeword
        bsc.Transmission()
        output = bsc.output
        print("通信路出力:\t\t", output)

        decoder0 = DecoderLR(K, N ,output, chaneltype, path)
        decoder0.DecodeMessage(P)
        hat_message0 = Message(K)
        hat_message0.message = decoder0.hat_message
        print("SCメッセージ推定値W:\t", hat_message0.message)

        print("本当のメッセージもどき:\t", encoder0.GetMessagePrime())

        error = np.bitwise_xor(message.message, hat_message0.message)
        print(" SC誤り数:", np.count_nonzero(error))

