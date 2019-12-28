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
from Decoder import ListDecoder_F
from binaryenthoropy import BinaryEntropy

if __name__ == '__main__':
    K = 128
    N = 256
    L = 8
    M = int(np.log2(N))
    chaneltype = "BSC"
    P = 0.06
    path = "./sort_I/sort_I_" + str(M) + "_" + str(P) + "_" + "20" + ".dat"
    # path ="./polarcode/"+"sort_I_" + str(M) + "_" + str(P) + "_" + "20" + ".dat"

    #kaisu = 100
    if len(sys.argv) == 2:
        if sys.argv[1] == "ber":
            kaisu = 500

            for P in [0.06]:
                # if False:
                #    with open("bsc_takusannnn.txt",mode='a',encoding='utf-8') as f:
                #        f.write("-----------------------P="+str(P)+", I(W)="+str(1-BinaryEntropy(P))+"----------------------------\n")
                #K = 1
                #N = 2
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

                        decoder0name = "_SC"
                        #start0 = time.time()
                        decoder0 = DecoderW(K, N, output, chaneltype, path, False)
                        decoder0.DecodeMessage(P)
                        hat_message0 = Message(K)
                        hat_message0.message = decoder0.hat_message
                        #end0 = time.time()

                        decoder1name = "SCL"
                        #start1 = time.time()
                        decoder1 = ListDecoder_F(K, N, L, output, chaneltype, path, False)
                        decoder1.DecodeMessage(P)
                        hat_message1 = Message(K)
                        hat_message1.message = decoder1.hat_message
                        #end1 = time.time()

                        error0 = np.bitwise_xor(message.message, hat_message0.message)
                        error1 = np.bitwise_xor(message.message, hat_message1.message)

                        eroorcount0 += np.count_nonzero(error0)
                        eroorcount1 += np.count_nonzero(error1)

                        frameerrorcout0 += 0 if np.count_nonzero(error0) == 0 else 1
                        frameerrorcout1 += 0 if np.count_nonzero(error1) == 0 else 1
                        print(i, "/", kaisu, "回目, ", 0 if np.count_nonzero(error0)
                              == 0 else 1, 0 if np.count_nonzero(error1) == 0 else 1)
                        #print("FSCL:", "{0:.5f}".format(end0-start0), "SCL", "{0:.5f}".format(end1-start1))
                    end = time.time()

                    if False:
                        with open("bsc_scltakusan.txt", mode='a', encoding='utf-8') as f:
                            f.write("K="+str(K)+", N=" +
                                    str(N)+", P="+str(P)+"\n")
                            f.write("送信: " + str(K*kaisu) +
                                    ", LR復号誤り: " + str(eroorcount1)+"\n")
                            f.write("FER__W: " +
                                    str(frameerrorcout0/kaisu)+"\n")
                            f.write("FER_LR: " +
                                    str(frameerrorcout1/kaisu)+"\n")
                            f.write("BER__W: " +
                                    str(eroorcount0/(K*kaisu))+"\n")
                            f.write("BER_LR: " +
                                    str(eroorcount1/(K*kaisu))+"\n")
                            f.write("実行時間: " + str(end-start)+"\n")

                    if True:
                        print("K="+str(K)+", N="+str(N)+", L="+str(L)+", P="+str(P))
                        print("送信メッセージ数: " + str(K*kaisu)+", " + decoder0name + "復号誤り: " +
                              str(eroorcount0)+", " + decoder1name + "復号誤り: " + str(eroorcount1))
                        print("FER_" + decoder0name + ": " + str(frameerrorcout0/kaisu))
                        print("FER_" + decoder1name + ": " + str(frameerrorcout1/kaisu))
                        print("BER_" + decoder0name + ": " + str(eroorcount0/(K*kaisu)))
                        print("BER_" + decoder1name + ": " + str(eroorcount1/(K*kaisu)))
                        print("実行時間: " + str(end-start))

    if len(sys.argv) == 1:
        print("K=", K, "N=", N, "L=", L)

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


        decoder1 = ListDecoder_F(K, N, L, output, chaneltype, path, False)
        #decoder1 = DecoderW(K, N, output, chaneltype, path)
        decoder1.DecodeMessage(P)
        hat_message1 = Message(K)
        hat_message1.message = decoder1.hat_message
        print("SCLメッセージ推定値:\t", hat_message1.message)

        decoder0 = DecoderW(K, N, output, chaneltype, path, False)
        decoder0.DecodeMessage(P)
        hat_message0 = Message(K)
        hat_message0.message = decoder0.hat_message
        print("SCメッセージ推定値:\t", hat_message0.message)

        print("本当のメッセージ:\t", message.message)

        error0 = np.bitwise_xor(message.message, hat_message0.message)
        print("SC誤り数:", np.count_nonzero(error0))
        error1 = np.bitwise_xor(message.message, hat_message1.message)
        print("SCL誤り数:", np.count_nonzero(error1))
