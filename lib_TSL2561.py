"""
adafruitのライブラリを使って測定

sudo apt update
sudo apt install python3-pip i2c-tools
pip3 install adafruit-circuitpython-tsl2561
"""

import time
import board
import busio
import adafruit_tsl2561

# I2Cバス初期化
i2c = busio.I2C(board.SCL, board.SDA)

# センサー初期化
sensor = adafruit_tsl2561.TSL2561(i2c)

# 感度の設定（必要に応じて）
sensor.enabled = True
sensor.gain = 0      # 0: 1x, 1: 16x
sensor.integration_time = 1  # 0: 13.7ms, 1: 101ms, 2: 402ms
time.sleep(1)

def lux_sensor():
    lux = sensor.lux
    return lux

def main():
    """
    TSL2561センサーのデータを取得して表示するメイン関数
    """
    # 照度補正値
    lux_hosei = 0.0

    try:
        print("センサー測定を開始します。Ctrl+Cで終了してください。")
        while True:
            lux = lux_sensor()
            lux = lux + lux_hosei
            print(f"照度: {lux:.0f} lux")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n測定を終了します。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
    main()