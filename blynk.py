
"""
2026/11/28
Blynk_PicoW.py
Raspberry Pi / Mac / Linux / 通常のPython 3

Blynkデータ送信専用モジュール

・Blynk CloudへのHTTPS送信
・SSL証明書検証
・ソケットタイムアウト対策
・通信エラー時はFalseを返す
・再試行なし
・ソケットを必ずクローズ

2026/11/28  EnvSensorPiのためのサンプルプログラム　データはランダムです。
"""

import socket
import ssl
import time
import config

# ------------------------------------------------------------
# 設定
# ------------------------------------------------------------

BLYNK_AUTH = config.BLYNK_token()

HOST = "blynk.cloud"
PORT = 443

# ソケットタイムアウト（秒）
SOCKET_TIMEOUT = 2

# HTTP応答タイムアウト（秒）
HTTP_TIMEOUT = 3


# ------------------------------------------------------------
# HTTPレスポンスのステータス行を取得
# ------------------------------------------------------------

def read_status_line(sock):

    data = b""
    start = time.monotonic()

    while True:

        # 応答待ち時間の確認
        if time.monotonic() - start > HTTP_TIMEOUT:
            raise TimeoutError("HTTP応答タイムアウト")

        ch = sock.recv(1)

        if not ch:
            break

        data += ch

        if ch == b"\n":
            break

        if len(data) > 128:
            raise OSError("HTTP応答データ異常")

    return data.decode("ascii", errors="replace").strip()


# ------------------------------------------------------------
# Blynkデータ送信
# ------------------------------------------------------------

def send_data(temp, humid, pressure, brightness, motion):

    if not BLYNK_AUTH or BLYNK_AUTH == "your token":
        print("Blynkトークン未設定")
        return False

    # Wi-Fi / ネットワーク接続確認
    try:
        pass
        # wifi_connect.keep_alive()

    except Exception as e:
        print("ネットワーク接続エラー:", repr(e))
        return False

    sock = None

    try:

        # ----------------------------------------------------
        # URL作成
        # ----------------------------------------------------

        from urllib.parse import urlencode

        params = {
            "token": BLYNK_AUTH,
            "V20": temp,
            "V21": humid,
            "V22": pressure,
            "V23": brightness,
            "V24": motion
        }

        path = "/external/api/batch/update?" + urlencode(params)

        # ----------------------------------------------------
        # DNS検索
        # ----------------------------------------------------

        print("Blynk送信開始")

        addr = socket.getaddrinfo(HOST, PORT, type=socket.SOCK_STREAM)[0][4]

        # ----------------------------------------------------
        # TCPソケット作成
        # ----------------------------------------------------

        raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        raw_sock.settimeout(SOCKET_TIMEOUT)

        raw_sock.connect(addr)

        # ----------------------------------------------------
        # SSL化
        # ----------------------------------------------------

        context = ssl.create_default_context()

        sock = context.wrap_socket(
            raw_sock,
            server_hostname=HOST
        )

        # ----------------------------------------------------
        # HTTPリクエスト送信
        # ----------------------------------------------------

        request = (
            "GET " + path + " HTTP/1.1\r\n"
            "Host: " + HOST + "\r\n"
            "Connection: close\r\n"
            "\r\n"
        )

        sock.sendall(request.encode("ascii"))

        # ----------------------------------------------------
        # HTTPステータス取得
        # ----------------------------------------------------

        status_line = read_status_line(sock)

        print("HTTP応答:", status_line)

        # ----------------------------------------------------
        # 結果判定
        # ----------------------------------------------------

        parts = status_line.split()

        if len(parts) >= 2:

            status = int(parts[1])

            if status == 200:
                print("Blynk送信成功")
                return True

            print("Blynk HTTPエラー:", status)
            return False

        print("HTTP応答形式エラー")
        return False

    except Exception as e:

        print("Blynk通信エラー:", repr(e))
        return False

    finally:

        # ----------------------------------------------------
        # ソケットを必ず閉じる
        # ----------------------------------------------------

        if sock is not None:

            try:
                sock.close()
            except Exception:
                pass

        print("Blynk送信処理終了")



# ------------------------------------------------------------
# メイン処理
# ------------------------------------------------------------

def main():

    import random
    # import lib_NTP

    # Wi-Fi接続
    # wifi_connect.connect()

    # NTP時刻設定
    # lib_NTP.NTP_set()

    # --------------------------------------------------------
    # メインループ
    # --------------------------------------------------------

    while True:

        try:

            # 次の正分まで待つ
            now = time.localtime()

            wait_sec = 60 - now.tm_sec

            print("次の正分まで待つ", wait_sec, "秒")

            time.sleep(wait_sec)

            # 毎正分に送信処理を開始
            print("送信開始:", time.localtime())

            # ------------------------------------------------
            # センサー読み取り（テストデータ）
            # ------------------------------------------------

            # temp, humid, pressure, brightness, motion = read_sensors()

            temp = 25.1 + random.randint(1, 5)
            humid = 40 + random.randint(1, 30)
            pressure = 999 + random.randint(1, 30)
            brightness = 50 + random.randint(1, 30)
            motion = random.randint(1, 10)

            print(temp, humid, pressure, brightness, motion)

            # ------------------------------------------------
            # ネットワーク維持
            # ------------------------------------------------

            # wifi_connect.keep_alive()

            # ------------------------------------------------
            # Blynk送信
            # ------------------------------------------------

            start_time = time.monotonic()

            result = send_data(
                temp,
                humid,
                pressure,
                brightness,
                motion
            )

            elapsed_time = time.monotonic() - start_time

            print("送信結果:", result)
            print("処理時間: {:.4f} 秒".format(elapsed_time))

        except KeyboardInterrupt:
            print("プログラムを終了します")
            break

        except Exception as e:
            print("処理エラー:", repr(e))

        print("-----------------")


if __name__ == "__main__":
    main()
