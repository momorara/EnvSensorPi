"""
GNU General Public License v2.0 
オリジナルは
https://github.com/paolosabatino/aht20
AHT10,AHT20,AHT30で動作するつもりで改変しています。
"""

"""
GNU General Public License v2.0

AHT10 / AHT20 / AHT30 温湿度センサー
オリジナル:
https://github.com/paolosabatino/aht20

I2C通信エラー対策
初期化確認・BUSYタイムアウト追加
測定データ取得の安定化
"""

from smbus2 import SMBus, i2c_msg
import time


class SensorAHTx0:
    I2C_ADDRESS = 0x38

    CMD_RESET = [0xBA]
    CMD_SETUP = [0xBE, 0x08, 0x00]
    CMD_READ  = [0xAC, 0x33, 0x00]

    STATUS_BUSY_BIT = 7
    STATUS_CALIBRATION_BIT = 3

    DATA_SCALING = 2**20

    # タイムアウト設定
    INIT_TIMEOUT = 1.0
    MEASURE_TIMEOUT = 1.0
    POLL_INTERVAL = 0.01

    def __init__(self, i2c_bus: SMBus,
                 device_address: int = I2C_ADDRESS):

        self.i2c_bus = i2c_bus
        self.device_address = device_address

        self.last_temperature = 0.0
        self.last_humidity = 0.0
        self.last_measurement_time = 0.0

        self._reset_and_initialize()

    def _read_status(self):
        """センサーのステータスを取得する。"""
        return self.i2c_bus.read_byte(self.device_address)

    def _reset_and_initialize(self):
        """センサーをリセットして初期化する。"""

        # ソフトウェアリセット
        self.i2c_bus.write_byte(
            self.device_address,
            self.CMD_RESET[0]
        )

        time.sleep(0.04)

        # 初期化コマンド
        self.i2c_bus.write_i2c_block_data(
            self.device_address,
            self.CMD_SETUP[0],
            self.CMD_SETUP[1:]
        )

        time.sleep(0.01)

        # キャリブレーション完了確認
        start_time = time.monotonic()

        while True:
            status = self._read_status()

            calibrated = (
                (status >> self.STATUS_CALIBRATION_BIT) & 1
            )

            if calibrated:
                return True

            if time.monotonic() - start_time >= self.INIT_TIMEOUT:
                raise TimeoutError(
                    "AHTx0 initialization timeout"
                )

            time.sleep(self.POLL_INTERVAL)

    def measure(self):
        """温度・湿度を測定する。"""

        # 測定開始
        self.i2c_bus.write_i2c_block_data(
            self.device_address,
            self.CMD_READ[0],
            self.CMD_READ[1:]
        )

        time.sleep(0.08)

        # BUSY解除待ち
        start_time = time.monotonic()

        while True:
            status = self._read_status()

            is_busy = (
                (status >> self.STATUS_BUSY_BIT) & 1
            )

            if not is_busy:
                break

            if time.monotonic() - start_time >= self.MEASURE_TIMEOUT:
                raise TimeoutError(
                    "AHTx0 measurement timeout"
                )

            time.sleep(self.POLL_INTERVAL)

        # 測定データを7バイト直接読み込む
        read_msg = i2c_msg.read(self.device_address, 7)
        self.i2c_bus.i2c_rdwr(read_msg)

        data = list(read_msg)

        if len(data) != 7:
            raise IOError("Invalid AHTx0 data length")

        # BUSY状態の再確認
        if (data[0] >> self.STATUS_BUSY_BIT) & 1:
            raise IOError("AHTx0 is still busy")

        # 湿度データ
        raw_humidity = (
            (data[1] << 12)
            | (data[2] << 4)
            | (data[3] >> 4)
        )

        # 温度データ
        raw_temperature = (
            ((data[3] & 0x0F) << 16)
            | (data[4] << 8)
            | data[5]
        )

        # 換算
        humidity = (
            raw_humidity / self.DATA_SCALING
        ) * 100

        temperature = (
            (raw_temperature / self.DATA_SCALING) * 200
        ) - 50

        # データ範囲確認
        if not (0 <= humidity <= 100):
            raise ValueError("Invalid humidity data")

        if not (-50 <= temperature <= 150):
            raise ValueError("Invalid temperature data")

        # 測定値保存
        self.last_temperature = temperature
        self.last_humidity = humidity
        self.last_measurement_time = time.time()

        return temperature, humidity


def main():
    """連続測定テスト"""

    bus_number = 1

    temp_hosei = 0
    humdy_hosei = 0

    i2c = None

    try:
        i2c = SMBus(bus_number)

        sensor = SensorAHTx0(i2c)

        print("AHTx0 measurement started.")

        while True:
            try:
                temperature, humidity = sensor.measure()

                temperature += temp_hosei
                humidity += humdy_hosei

                print(
                    f"Temp: {temperature:.1f} °C, "
                    f"Humi: {humidity:.0f} %"
                )

            except KeyboardInterrupt:
                raise

            except Exception as error:
                print(f"Measurement error: {error}")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nMeasurement stopped.")

    except Exception as error:
        print(f"Sensor error: {error}")

    finally:
        if i2c is not None:
            i2c.close()


if __name__ == "__main__":
    main()
