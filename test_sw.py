#!/usr/bin/python

"""
###########################################################################
スイッチの状態を確認する。

#Filename      :test_sw.py

#Update        :2019/11/02
2023/9/22   タクトスイッチ　ソフトプルダウンとする。
2025/01/07  pi5のためgpiozeroに置き換え
2025/08/21  環境測定2用
############################################################################
"""
from gpiozero import Button
import time

# SW_1 = Button(5,pull_up=False)
SW = Button(6,pull_up=False)

#print message at the begining ---custom function
def print_message():
    print ('|********************************|')
    print ('|   switch 監視　　　　　          |')
    print ('|********************************|\n')
    print ('Program is running...')
    print ('Please press Ctrl+C to end the program...')


#read SW_PI_1's level
# def ReadSW_1():
#     if SW_1.is_pressed:
#         sw_ = 'on'
#     else:
#         sw_ = 'off'
#     return sw_

#read SW_PI_2's level
def ReadSW():
    if SW.is_pressed:
        sw_ = 'on'
    else:
        sw_ = 'off'
    return sw_

#main function
def main():
    loop_n = 0
    #print info
    sw_ = 'off'
    print_message()
    while True:
        # sw_ = ReadSW_1()
        # if sw_ =='off':
        #     print('sw_1_off')
            
        # else:
        #     print('sw_1_on')
        # time.sleep(1)

        sw_ = ReadSW()
        if sw_ =='off':
            print('sw_off')
            
        else:
            print('sw_on')
        time.sleep(1)
    pass

#
# if run this script directly ,do:
if __name__ == '__main__':
    try:
        main()
    #when 'Ctrl+C' is pressed,child program destroy() will be executed.
    except KeyboardInterrupt:
        pass
    except ValueError as e:
        print(e)
