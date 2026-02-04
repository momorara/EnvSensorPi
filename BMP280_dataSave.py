# –– coding: utf-8 –
#!/usr/bin/python
"""
BMPセンサーから気圧情報をとりだし、ファイル保存する

press_data.txt
BMP180_dataSave.py  python2で実行のこと
BMP180_dataSave3.py  python3で実行のこと

by.kawabata

20230812    BMP180 と BMP280 を意識せずに使えるようにしたい。
20240820    初回低い個体への対応を990未満とした
2025/01/12  adafruitライブラリを使わないプログラム
            BMP280専用

"""

# 補正値
hosei = 0.0

# import lib_path
# path = lib_path.get_path()
# print(path)
# cronの場合は指定が必要
path = '/home/pi/envsensor/'


import datetime
import time

from lib_BMP280 import BMP280
bmp280 = BMP280()
temp, press = bmp280.read_sensor_data()

press = round(press,2)

print(f"Temperature: {temp:.2f} °C, Pressure: {press:.2f} hPa")


print('測定値',end='', flush=True)
print('Pressure = ',press,'hPa' )

print('補正値',end='', flush=True)
print(hosei)

print('補正後',end='', flush=True)
press = press + hosei
print(f"Pressure = {press:.2f}hPa" )


time.sleep(0.5)

dt_now = datetime.datetime.now()
################## press ###################
# # 最新のデータを一つだけ入れたファイルを作る
with open(path + 'press_data.txt', mode='a') as f:
    f.write(f"{dt_now}, {press:.2f}\n")
with open(path + 'press_data_last.txt', mode='w') as f:
    f.write(f"{press:.2f}\n")
############################################

