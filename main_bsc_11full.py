# -*- coding: utf-8 -*-
from subprocess import check_call
import numpy as np
import sys
import time
#from tkinter import messagebox

from message import Message
from Encoder import Encoder
from chanel import BSC
from Decoder import DecoderW
from Decoder import DecoderLR
from Decoder import ListDecoder
from Decoder import ListDecoder_F
from Decoder import ListDecoder_CRC
from CRC import CRC_Encoder
from CRC import CRC_Detector


if __name__ == '__main__':
    k = 128
    r = 6 
    K = k + r
    N = 256
    Nlist = [N]
    L = 4
    Llist = [L]
    M = int(np.log2(N))
    chaneltype = "BSC"
    P = 0.09
    Plist = [P]
    path = "./sort_I/sort_I_" + str(M) + "_" + str(P) + "_" + "20" + ".dat"
    # path ="./polarcode/"+"sort_I_" + str(M) + "_" + str(P) + "_" + "20" + ".dat"
    SaveResult = True
    kaisu = 5000
    result_file_name = "./re/"+str(N)+"_"+str(P)+"_"+str(kaisu)+"full.txt"

    if len(sys.argv) == 2 and sys.argv[1] == "ber":
        for i in range(1):
            for P in Plist:
                if SaveResult:
                    with open(result_file_name, mode='a', encoding='utf-8') as f:
                        f.write("-----------------------P="+str(P)+"----------------------------\n")
                for L in Llist:
                    for N in Nlist:
                        k = N//2
                        K = k + r
                        eroorcount0 = 0
                        frameerrorcout0 = 0
                        eroorcount1 = 0
                        frameerrorcout1 = 0

                        path = path = "./sort_I/sort_I_" + str(int(np.log2(N))) + "_" + str(P) + "_" + "20" + ".dat"
                        start = time.time()
                        for i in range(kaisu):
                            message = Message(k)
                            message.MakeMessage()

                            crcenc = CRC_Encoder(message.message, r)
                            crcenc.Encode()

                            encoder0 = Encoder(K, N, crcenc.codeword, path, False)
                            encoder0.MakeCodeworde()

                            bsc = BSC(P)
                            bsc.input = encoder0.codeword
                            bsc.Transmission()
                            output = bsc.output

                            # decoder0name = "_SC"
                            # start0 = time.time()
                            # decoder0 = ListDecoder_TwoCRC(K, N, L, r, K//2, output, chaneltype, path, False)
                            # decoder0.DecodeMessage(P)
                            # hat_message0 = Message(K)
                            # hat_message0.message = decoder0.hat_message
                            # end0 = time.time()

                            decoder1name = "OneCRC-SCL"
                            # start1 = time.time()
                            decoder1 = ListDecoder_CRC(K, N, L, r, output, chaneltype, path, False)
                            decoder1.DecodeMessage(P)
                            hat_message1 = Message(k)
                            hat_message1.message = decoder1.hat_message
                            # end1 = time.time()

                            # error0 = np.bitwise_xor(message.message, hat_message0.message)
                            error1 = np.bitwise_xor(message.message, hat_message1.message[:k])

                            # eroorcount0 += np.count_nonzero(error0)
                            eroorcount1 += np.count_nonzero(error1)

                            # frameerrorcout0 += 0 if np.count_nonzero(error0) == 0 else 1
                            frameerrorcout1 += 0 if np.count_nonzero(error1) == 0 else 1
                            if i%20 == 0:
                                print(i, "/", kaisu, "回目, ",
                                    #       0 if np.count_nonzero(error0) == 0 else 1,
                                    #0 if np.count_nonzero(error1) == 0 else 1
                                    )
                            
                            # print("FSCL:", "{0:.5f}".format(end0-start0), "SCL", "{0:.5f}".format(end1-start1))
                        end = time.time()

                        if SaveResult:
                            with open(result_file_name, mode='a', encoding='utf-8') as f:
                                f.write("K="+str(k)+", N="+str(N) + ", r=" + str(r) + ", L="+str(L)+", P="+str(P)+"\n")
                                # f.write("送信メッセージ数: " + str(K*kaisu)+", " + decoder0name + "復号誤り: "
                                #       + str(eroorcount0)+", " + decoder1name + "復号誤り: " + str(eroorcount1))
                                f.write("回数: "+str(kaisu)+", 送信メッセージ数: " + str(k*kaisu)+", " + decoder1name +
                                        ", フレームエラー数" + str(frameerrorcout1)+", ビットエラー数: " + str(eroorcount1)+"\n")
                                #f.write("FER_" + decoder0name + ": " + str(frameerrorcout0/kaisu)+"\n")
                                f.write("FER_" + decoder1name + ": " + str(frameerrorcout1/kaisu)+"\n")
                                #f.write("BER_" + decoder0name + ": " + str(eroorcount0/(k*kaisu))+"\n")
                                f.write("BER_" + decoder1name + ": " + str(eroorcount1/(k*kaisu))+"\n")
                                f.write("実行時間: " + str(end-start)+"\n")

                        # if True:
                        #     with open(result_file_name, mode='a', encoding='utf-8') as f:
                        #         f.write(str(kaisu)+","+str(frameerrorcout1)+","+str(frameerrorcout1/kaisu)+str(k*kaisu)+"," + str(eroorcount1)+"\n")

                        if True:
                            print("K="+str(k)+", N="+str(N) + ", r=" + str(r) + ", L="+str(L)+", P="+str(P))
                            # print("送信メッセージ数: " + str(K*kaisu)+", " + decoder0name + "復号誤り: " +
                            #      str(eroorcount0)+", " + decoder1name + "復号誤り: " + str(eroorcount1))
                            print("回数: "+str(kaisu)+", 送信メッセージ数: " + str(k*kaisu)+", " + decoder1name +
                                  ", フレームエラー数" + str(frameerrorcout1)+", ビットエラー数: " + str(eroorcount1))
                            #print("FER_" + decoder0name + ": " + str(frameerrorcout0/kaisu))
                            print("FER_" + decoder1name + ": " + str(frameerrorcout1/kaisu))
                            #print("BER_" + decoder0name + ": " + str(eroorcount0/(k*kaisu)))
                            print("BER_" + decoder1name + ": " + str(eroorcount1/(k*kaisu)))
                            print("実行時間: " + str(end-start))

    if len(sys.argv) == 1:
        print("K=", k, "N=", N, "r=", r, "L=", L)

        message = Message(k)
        message.MakeMessage()
        print("メッセージ:\t\t", message.message)

        crcenc = CRC_Encoder(message.message, r)
        crcenc.Encode()
        print("CRC付与:\t\t", crcenc.codeword)

        encoder0 = Encoder(K, N, crcenc.codeword, path)
        encoder0.MakeCodeworde()
        print("符号語:\t\t\t", encoder0.codeword)

        bsc = BSC(P)
        bsc.input = encoder0.codeword
        bsc.Transmission()
        output = bsc.output
        print("通信路出力:\t\t", output)

        # decoder0 = ListDecoder_F(K, N, L, output, chaneltype, path, False)
        # decoder0.DecodeMessage(P)
        # hat_message0 = Message(K)
        # hat_message0.message = decoder0.hat_message
        # print("  SCLメッセージ推定値:\t", hat_message1.message)

        decoder1 = ListDecoder_CRC(K, N, L, r, output, chaneltype, path, False)
        decoder1.DecodeMessage(P)
        hat_message1 = Message(K)
        hat_message1.message = decoder1.hat_message[:k]
        print("CASCLメッセージ推定値:\t", hat_message1.message)

        # print("本当のメッセージ:\t", message.message)

        # error0 = np.bitwise_xor(message.message, hat_message0.message)
        # print("  SCL誤り数:", np.count_nonzero(error0))
        error1 = np.bitwise_xor(message.message, hat_message1.message)
        print("CASCL誤り数:", np.count_nonzero(error1))