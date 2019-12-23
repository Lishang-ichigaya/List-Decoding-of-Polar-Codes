from subprocess import check_call
import numpy as np
import sys
import time
from tkinter import messagebox

from message import Message
#from codeword import CodeWorde
from Encoder import Encoder
from chanel import BSC
from Decoder import Decoder
from Decoder import ListDecoder

if __name__ == '__main__':
    K = 16
    N = 32
    L = 4
    M = int(np.log2(N))
    chaneltype = "BSC"
    P = 0.11
    path = "./sort_I/sort_I_" + str(M) + "_" + str(P) + "_" + "20" + ".dat"
    # path ="./polarcode/"+"sort_I_" + str(M) + "_" + str(P) + "_" + "20" + ".dat"

    kaisu = 5000
    if len(sys.argv) == 2:
        # 相互情報量を計算する場合は 'c' オプションをつける
        if sys.argv[1] == "c":
            check_call(["./sort_I/calIdmcDp.exe", str(M), str(P), "20"])

        if sys.argv[1] == "ber":
            eroorcount0 = 0
            eroorcount1 = 0
            frameerrorcout0 = 0
            frameerrorcout1 = 0
            

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
            
                decoder0 = Decoder(K, N ,output, chaneltype, path ,False)
                decoder0.DecodeMessage(P)
                decoder1 = ListDecoder(K, N, L, output, chaneltype, path, False)
                decoder1.DecodeMessage(P)

                error0 = np.bitwise_xor(message.message, decoder0.hat_message)
                eroorcount0 += np.count_nonzero(error0)
                error1 = np.bitwise_xor(message.message, decoder1.hat_message)
                eroorcount1 += np.count_nonzero(error1)


                frameerrorcout0 += 0 if np.count_nonzero(error0) == 0 else 1
                frameerrorcout1 += 0 if np.count_nonzero(error1) == 0 else 1
                print(i, "/", kaisu, "回目, ",
                      0 if np.count_nonzero(error0) == 0 else 1)
            end = time.time()

            print("送信:", K*kaisu, " SC復号誤り:", eroorcount0,"SCL復号誤り:", eroorcount1)
            print("SC__FER: ", frameerrorcout0/kaisu)
            print("SCL_FER: ", frameerrorcout1/kaisu)
            print("SC__BER: ", eroorcount0/(K*kaisu))
            print("SCL_BER: ", eroorcount1/(K*kaisu))
            print("実行時間: ", end-start)

            messagebox.showinfo('終わったよ', '終わったよ')

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


        decoder1 = ListDecoder(K, N, L, output, chaneltype, path)
        decoder1.DecodeMessage(P)
        hat_message1 = Message(K)
        hat_message1.message = decoder1.hat_message
        print("SCLメッセージ推定値:\t", hat_message1.message)

        decoder0 = Decoder(K, N ,output, chaneltype, path)
        decoder0.DecodeMessage(P)
        hat_message0 = Message(K)
        hat_message0.message = decoder0.hat_message
        print(" SCメッセージ推定値:\t", hat_message0.message)

        print("本当のメッセージもどき:\t", encoder0.GetMessagePrime())

        error = np.bitwise_xor(message.message, hat_message0.message)
        print(" SC誤り数:", np.count_nonzero(error))

        error = np.bitwise_xor(message.message, hat_message1.message)
        print("SCL誤り数:", np.count_nonzero(error))
