import win32com.client
import pythoncom
import datetime
import time
import os
# import numpy
# from numpy import *
class MiniIo:
    def __init__(self):
        self.io = win32com.client.Dispatch("MCL_USB_To_IO.USB_IO")
        cn = self.io.Connect()
        print(cn)

        self.one_dB = b"1000000"
        self.two_dB = b"1100000"
        self.four_dB = b"1110000"
        self.eight_dB = b"1111000"
        self.sixteen_dB = b"1111110"

    def binary_string_to_dec(self, string):
        rev = string[::-1]
        integer = int(rev, 2)
        return integer

    def set_bytes_to_a(self, bytes):
        res = self.io.Set_ByteA(bytes)
        print(res)

    def set_bytes_to_b(self, bytes):
        res = self.io.Set_ByteB(bytes)
        print(res)
