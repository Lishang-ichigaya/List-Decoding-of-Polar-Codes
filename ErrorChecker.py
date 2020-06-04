# -*- coding: utf-8 -*-
import numpy as np

class ErrorChecker:
    def __init__(self):
        pass

    @classmethod
    def IsDecodeError(self, true_message, estimated_message):
        """
        メッセージの推定値に誤りが生じたか確認するメソッド\n
        true_message: 符号化する前のメッセージ
        estimated_message: デコーダで推定したメッセージ
        """
        error = true_message ^ estimated_message
        biterror = np.count_nonzero(error)
        is_flameerror = True if biterror != 0 else False

        return is_flameerror, biterror

if __name__ == "__main__":
    true = np.array([0,0,1,1,0,0,1,0], dtype=np.uint8)
    esti = np.array([0,0,1,1,0,0,1,0], dtype=np.uint8)

    a = ErrorChecker.IsDecodeError(true, esti)
    print(a[0])