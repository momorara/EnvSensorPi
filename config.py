# -*- coding: utf-8 -*-
#!/usr/bin/python3
"""
ID PASS LINE_token
2023/5/7    lib化
2023/5/20   名称をconfig.pyとする
            測定周期を追加
2023/6/10   wifi 使用/不使用を追加
2023/6/19   補正値を持つ
v1.0
2024/09/08  mail追加 2
2026/11/14  sensorPicoとmimamoriPicoのなるべく共通化
            メール送信を削除
2026/11/28  EnvSensorPiのためのサンプルプログラム　データはランダムです。
"""

def ID_PASS():
    # wifiのssidとパスワード
    # あなたのwifiの設定に変更してください。
    ssid        = 'your ssid'
    password    = 'your password'

    return ssid,password


def hosei():
    # センサーのオフセット誤差を補正する補正値です。
    temp  = 0
    humdi = 0
    press = 0
    return temp,humdi,press

def BLYNK_token():
    BLYNK_AUTH = "your token"
    # your tokenの場合は、送信しない
    #------------ 
    BLYNK_AUTH = "your token"
    return BLYNK_AUTH


def main():
    print(ID_PASS())
    print(hosei())

if __name__=='__main__':
    main()