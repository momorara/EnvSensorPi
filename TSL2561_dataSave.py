# –– coding: utf-8 –
#!/usr/bin/python
"""
BMPセンサーから気圧情報をとりだし、ファイル保存する

lux_data.txt
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

import lib_TSL2561
lux = lib_TSL2561.lux_sensor()
print(f"lux: {lux:.0f} ")

lux = round(lux,2)

print('測定値',end='', flush=True)
print('lux = ',lux)

print('補正値',end='', flush=True)
print(hosei)

print('補正後',end='', flush=True)
lux = lux + hosei
print('lux = ',lux)

print('補正後int ',end='', flush=True)
print(f"lux = {lux:.0f}" )

time.sleep(0.5)

dt_now = datetime.datetime.now()
################## lux ###################
# # 最新のデータを一つだけ入れたファイルを作る
with open(path + 'lux_data.txt', mode='a') as f:
    f.write(f"{dt_now}, {lux:.2f}\n")
with open(path + 'lux_data_last.txt', mode='w') as f:
    f.write(f"{lux:.2f}\n")
############################################

