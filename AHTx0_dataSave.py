# -*- coding: utf-8 -*-
#!/usr/bin/python3

# AHT10_02.py
"""
pip install adafruit-circuitpython-ahtx0
でインストールすると使えます。MITライセンスとのこと

2021/03/30  ライブラリを改造してsensorHATで使えるようにする
            zeroで使えないDHT11の代替え
            1度だけ測定して、ファイルに書き込む
2021/04/02  i2c接続がない場合のエラー処理を追加
2021/04/25  board,busio,adafruit_ahtx0を使わない方法
    02
2022/03/06  AHT10がない場合に、BMPの温度を使用する。
2022/12/04  補正値の整備
2023/12/19  最近購入したAHT10がラズパイで読み取れなくなったので、
            新しいドライバを入れて対応した。
2023/12/21  AHT30でもデータ取得できた。
2025/01/12  adafruitライブラリを使わないプログラム
2025/08/28  保存桁数調整
"""

# 補正値
temp_hosei  = 0
humdy_hosei = 0

# import lib_path
# path = lib_path.get_path()
# print(path)
# cronの場合は指定が必要
path = '/home/pi/envsensor/'

import time
import datetime
from lib_AHTx0 import SensorAHTx0
from smbus2 import SMBus


def data_read():

    
    bus_number = 1
    i2c = SMBus(bus_number)
    sensor = SensorAHTx0(i2c)
    temp, humdy = sensor.measure()

    return temp,humdy


# i2c接続がない場合のエラーでは何もせずに終了する。


try:
    temp,humdy = data_read()
except:
    time.sleep(2)
    temp,humdy = data_read()

temp = round(temp,2)
humdy = round(humdy,2)

print('測定値',end='', flush=True)
print("Temperature: %0.1f C" % temp, end='', flush=True)
print("   Humidity: %0.0f %%" % humdy)

print('補正値        ',end='', flush=True)
print('温度:',temp_hosei,'           湿度:',humdy_hosei)

print('補正後',end='', flush=True)
temp = temp + temp_hosei
humdy = humdy + humdy_hosei
print("Temperature: %0.1f C" % temp, end='', flush=True)
print("   Humidity: %0.0f %%" % humdy)

dt_now = datetime.datetime.now()

################## temp ###################
# # 最新のデータを一つだけ入れたファイルを作る
with open(path + 'temp_data.txt', mode='a') as f:
    f.write(f"{dt_now}, {temp:.2f}\n")
with open(path + 'temp_data_last.txt', mode='w') as f:
    f.write(f"{temp:.2f}\n")
############################################

################## humdy ###################
# # 最新のデータを一つだけ入れたファイルを作る
with open(path + 'humdy_data.txt', mode='a') as f:
    f.write(f"{dt_now}, {humdy:.2f}\n")
with open(path + 'humdy_data_last.txt', mode='w') as f:
    f.write(f"{humdy:.2f}\n")
############################################
