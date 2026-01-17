# kudou_test 関数詳細説明

このドキュメントでは、`kudou_test` ディレクトリで定義されている関数の詳細を説明します。

---

## `is_raspberry_pi() -> bool`

**ファイル:** `hardware_import.py`

Raspberry Pi環境かどうかを判定する関数。

**戻り値:**
- `True`: Raspberry Pi環境の場合
- `False`: それ以外（Docker環境など）の場合

**判定方法:**
1. `/proc/cpuinfo` を読み込み、'Raspberry Pi' または 'BCM' が含まれているか確認
2. 環境変数 `USE_MOCK_HARDWARE` が設定されている場合は、その値に従う
3. デフォルトでは `False` を返す（Docker環境を想定）

**使用例:**
```python
from hardware_import import is_raspberry_pi
if is_raspberry_pi():
    print("Raspberry Pi環境です")
else:
    print("モック環境です")
```

---

## `set_us(ch, us)`

**ファイル:** `drive_test.py`

μs（マイクロ秒）をduty_cycle値に変換してPCA9685のチャンネルに設定する関数。

**パラメータ:**
- `ch`: PCA9685のチャンネルオブジェクト
- `us`: パルス幅（マイクロ秒）

**計算式:**
```python
duty_cycle = int(us / 20000 * 65535)
```

**説明:**
- PCA9685のPWM周期は20ms（50Hz）を想定
- duty_cycle値は0-65535の範囲
- μsをduty_cycle値に変換してチャンネルに設定

**使用例:**
```python
set_us(esc, 1500)   # ニュートラル（1500μs）
set_us(esc, 1600)   # 前進（1600μs）
set_us(servo, 1300) # サーボ左（1300μs）
set_us(servo, 1500) # サーボ中央（1500μs）
set_us(servo, 1700) # サーボ右（1700μs）
```

**ESCの一般的な値:**
- 1500μs: ニュートラル（停止）
- 1600μs: 前進（低速）
- 1450μs: 後退

**サーボの一般的な値:**
- 1300μs: 左
- 1500μs: 中央
- 1700μs: 右
