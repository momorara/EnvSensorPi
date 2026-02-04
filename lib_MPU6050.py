#!/usr/bin/python
# -*- coding: utf-8 -*-

# MPU6050_2_2.py

# http://manabi.science/library/2017/02121501/

"""
2020/08/27  小数点があるとわかりにくいので、整数にする。
2020/08/28  布団の下にセンサーを入れて、寝返りを検知したい。
            これにより、寝返りを検知出来たらその間はレム睡眠と判定。
2020/09/21  ユーザー名変更に対応
2026/01/02  EnvSensorPi用のサンプルプログラムとして修正

6軸センサー MPU6050は
GYRO（ジャイロセンサ）とACCEL（加速度センサ）があり

加速度センサは「どの向きに、どれくらい強く動いているか」
ジャイロセンサ「どの方向に、どれくらい速く回っているか」
を測定しています。
仮に水平な面に静止している状態では、
GYRO x,y,z = 0
ACCEL x,y = 0 z = 9.8
と表示されます。揺らぎ誤差があるので、少しはずれます。

本ライブラリでは、揺らぎ誤差の補正はしていないので、実際に使用する際には補正をしてください。

"""

import smbus            # use I2C
from time import sleep  # time module


### define #############################################################
DEV_ADDR = 0x68         # device address
PWR_MGMT_1 = 0x6b       # Power Management 1
ACCEL_XOUT = 0x3b       # Axel X-axis
ACCEL_YOUT = 0x3d       # Axel Y-axis
ACCEL_ZOUT = 0x3f       # Axel Z-axis
TEMP_OUT = 0x41         # Temperature
GYRO_XOUT = 0x43        # Gyro X-axis
GYRO_YOUT = 0x45        # Gyro Y-axis
GYRO_ZOUT = 0x47        # Gyro Z-axis
 
# 1byte read
def read_byte( addr ):
    return bus.read_byte_data( DEV_ADDR, addr )
 
# 2byte read
def read_word( addr ):
    high = read_byte( addr   )
    low  = read_byte( addr+1 )
    return (high << 8) + low
 
# Sensor data read
def read_word_sensor( addr ):
    val = read_word( addr )
    if( val < 0x8000 ):
        return val # positive value
    else:
        return val - 65536 # negative value
 
# Get Temperature
def get_temp():
    temp = read_word_sensor( TEMP_OUT )
    # offset = -521 @ 35℃
    return ( temp + 521 ) / 340.0 + 35.0
 
# Get Gyro data (raw value)
def get_gyro_data_lsb():
    x = read_word_sensor( GYRO_XOUT )
    y = read_word_sensor( GYRO_YOUT )
    z = read_word_sensor( GYRO_ZOUT )
    return [ x, y, z ]

# Get Gyro data (deg/s)
def get_gyro_data_deg():
    x,y,z = get_gyro_data_lsb()
    # Sensitivity = 131 LSB/(deg/s), @cf datasheet
    x = x / 131.0
    y = y / 131.0
    z = z / 131.0
    return [ x, y, z ]
 
# Get Axel data (raw value)
def get_accel_data_lsb():
    x = read_word_sensor( ACCEL_XOUT )
    y = read_word_sensor( ACCEL_YOUT )
    z = read_word_sensor( ACCEL_ZOUT )
    return [ x, y, z ]

# Get Axel data (G)
# 加速度を重力加速度値に変換 1G = 9.8 m/s²
def get_accel_data_g():
    x,y,z = get_accel_data_lsb()
    # Sensitivity = 16384 LSB/G, @cf datasheet
    x = x / 16384.0 * 9.8 
    y = y / 16384.0 * 9.8
    z = z / 16384.0 * 9.8
    return [x, y, z]
 
def data_read():
    # 
    gyro_x,gyro_y,gyro_z = get_gyro_data_deg()
    accel_x,accel_y,accl_z = get_accel_data_g()
    
    return gyro_x,gyro_y,gyro_z,accel_x,accel_y,accl_z


### Main function ######################################################
bus = smbus.SMBus( 1 )
bus.write_byte_data( DEV_ADDR, PWR_MGMT_1, 0 )


while True:

    gyro_x,gyro_y,gyro_z,accel_x,accel_y,accel_z = data_read()
    print(
    f"GYRO [deg/s] X:{gyro_x:6.1f} Y:{gyro_y:6.1f} Z:{gyro_z:6.1f} | "
    f"ACCEL[m/s²] X:{accel_x:6.2f} Y:{accel_y:6.2f} Z:{accel_z:6.2f}"
    )

    sleep(0.5)