#Simple MPU6050 Demo on Raspberry pi 2 using ITG-MPU breakout board (MPU6050)
#This breakout board from aliexpress for $1.50. 40pin old IDE cable used to connect to raspi2
#no interrupt, +vcc of the board is connected to +5v of raspi2
#only sda, scl connected to raspi2.
#MPU data accessed regularly every 10ms (.01sec), sleep time reduced to allow data processing and draw.
#By Opata Padmasiri  
#codes for reading data from MPU6050 and complementary filter taken from the following blog: 
#http://blog.bitify.co.uk/2013/11/reading-data-from-mpu-6050-on-raspberry.html

#!/usr/bin/python
# pygame：画面表示・キー入力用
# sys：プログラム終了用
import pygame, sys
from pygame.locals import *

# smbus：I2C通信（MPU6050と通信するため）
import smbus

# math：三角関数や平方根を使う
import math

# time：一定時間待つため
import time  

# ==================================
# pygame の初期化
# 画面表示やキー入力を使う準備
# ==================================
pygame.init()
  
# ==================================
# ウィンドウの設定
# サイズ：400×300
# ==================================
WINDOW = pygame.display.set_mode((400, 300), 0, 32)
pygame.display.set_caption('MPU_6050 Demo')
  
# ==================================
# 色の定義（RGB）
# ==================================
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)
  
# 最初に画面を白で塗りつぶす
WINDOW.fill(WHITE)

# ==================================
# MPU6050 のレジスタ設定
# ==================================
# 電源管理レジスタ
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c
 
# ジャイロ・加速度のスケール値
gyro_scale = 131.0
accel_scale = 16384.0
 
# MPU6050 の I2C アドレス（通常は 0x68）
address = 0x68

# I2C バスの指定（Raspberry Pi は 1）
bus = smbus.SMBus(1)

# ==================================
# MPU6050 は初期状態ではスリープしているため
# スリープ解除（0を書き込む）
# ==================================
bus.write_byte_data(address, power_mgmt_1, 0)

# ==================================
# MPU6050 から
# ジャイロ・加速度のデータをまとめて読む関数
# ==================================
def read_all():
    # ジャイロデータ（6バイト）
    raw_gyro_data = bus.read_i2c_block_data(address, 0x43, 6)

    # 加速度データ（6バイト）
    raw_accel_data = bus.read_i2c_block_data(address, 0x3b, 6)

    # ジャイロ値をスケール変換
    gyro_scaled_x = twos_compliment((raw_gyro_data[0] << 8) + raw_gyro_data[1]) / gyro_scale
    gyro_scaled_y = twos_compliment((raw_gyro_data[2] << 8) + raw_gyro_data[3]) / gyro_scale
    gyro_scaled_z = twos_compliment((raw_gyro_data[4] << 8) + raw_gyro_data[5]) / gyro_scale
 
    # 加速度値をスケール変換
    accel_scaled_x = twos_compliment((raw_accel_data[0] << 8) + raw_accel_data[1]) / accel_scale
    accel_scaled_y = twos_compliment((raw_accel_data[2] << 8) + raw_accel_data[3]) / accel_scale
    accel_scaled_z = twos_compliment((raw_accel_data[4] << 8) + raw_accel_data[5]) / accel_scale
    
    # 6つの値をまとめて返す
    return (
        gyro_scaled_x, gyro_scaled_y, gyro_scaled_z,
        accel_scaled_x, accel_scaled_y, accel_scaled_z
    )

# ==================================
# 2の補数変換
# MPU6050 のデータを正しい数値に直す
# ==================================
def twos_compliment(val):
    if val >= 0x8000:
        return -((65535 - val) + 1)
    else:
        return val

# ==================================
# Y軸の回転角を計算（度）
# ==================================
def get_y_rotation(x, y, z):
    radians = math.atan2(x, dist(y, z))
    return -math.degrees(radians)

# ==================================
# X軸の回転角を計算（度）
# ==================================
def get_x_rotation(x, y, z):
    radians = math.atan2(y, dist(x, z))
    return math.degrees(radians)

# ==================================
# 2点間の距離を計算
# ==================================
def dist(a, b):
    return math.sqrt((a * a) + (b * b))

# ==================================
# メイン処理
# ==================================
def main():
    
    # 相補フィルタの係数
    # ジャイロを主に信頼する割合
    K = 0.98
    K1 = 1 - K

    # ループの時間間隔（秒）
    time_diff = 0.01

    # 最初のセンサ値を取得
    (gyro_scaled_x, gyro_scaled_y, gyro_scaled_z,
     accel_scaled_x, accel_scaled_y, accel_scaled_z) = read_all()

    # 加速度から初期角度を計算
    last_x = get_x_rotation(accel_scaled_x, accel_scaled_y, accel_scaled_z)
    last_y = get_y_rotation(accel_scaled_x, accel_scaled_y, accel_scaled_z)

    # ジャイロのオフセット（ドリフト対策）
    gyro_offset_x = gyro_scaled_x
    gyro_offset_y = gyro_scaled_y

    # ジャイロ角度の積算値
    gyro_total_x = last_x - gyro_offset_x
    gyro_total_y = last_y - gyro_offset_y    

    print("ループ開始 (qキーで終了します)")

    # ==================================
    # メインループ
    # ==================================
    while True:
        
        # -------- 終了処理 --------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

        # センサ読み取りの間隔を調整
        time.sleep(time_diff - 0.005)

        # 最新のセンサ値を取得
        (gyro_scaled_x, gyro_scaled_y, gyro_scaled_z,
         accel_scaled_x, accel_scaled_y, accel_scaled_z) = read_all()
        
        # オフセット補正
        gyro_scaled_x -= gyro_offset_x
        gyro_scaled_y -= gyro_offset_y
        
        # 角度変化量を計算
        gyro_x_delta = gyro_scaled_x * time_diff
        gyro_y_delta = gyro_scaled_y * time_diff

        # 角度を積算
        gyro_total_x += gyro_x_delta
        gyro_total_y += gyro_y_delta

        # 加速度から角度を再計算
        rotation_x = get_x_rotation(accel_scaled_x, accel_scaled_y, accel_scaled_z)
        rotation_y = get_y_rotation(accel_scaled_x, accel_scaled_y, accel_scaled_z)
    
        # 相補フィルタで角度を合成
        last_x = K * (last_x + gyro_x_delta) + (K1 * rotation_x)
        last_y = K * (last_y + gyro_y_delta) + (K1 * rotation_y)
        
        # 動作確認用（点を表示）
        print('.', end='', flush=True)
        
        # Y軸角度をラジアンに変換
        delta_y = math.radians(last_y)
    
        # 線の太さ（X軸の傾きで変化）
        z = 2 * int(last_x)

        # 傾きの向きで色を変える
        if z < 0:
            z = -z
            COLOR = RED
        else:
            COLOR = BLUE

        if z == 0:
            z = 1

        # 線の両端の座標を計算
        x1 = 200 - (100 * math.cos(delta_y))
        y1 = 150 + (100 * math.sin(delta_y))	
        x2 = 200 + (100 * math.cos(delta_y))
        y2 = 150 - (100 * math.sin(delta_y))
        
        # 画面を白でクリア
        WINDOW.fill(WHITE)

        # 傾きを表す線を描画（太さ z）
        pygame.draw.line(WINDOW, COLOR, (x1, y1), (x2, y2), z)

        # 画面を更新
        pygame.display.update()

# ==================================
# プログラムの開始点
# ==================================
if __name__ == "__main__":
    main()
