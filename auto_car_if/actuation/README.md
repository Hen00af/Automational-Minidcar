# CarDriver 使用方法ガイド

`CarDriver`クラスは、PCA9685 I2C PWMドライバーを使用して、自律走行ミニカーのステアリングサーボとDCモーターを制御するためのクラスです。

## Prerequisites（前提条件）

### ハードウェア接続

#### 全体構成図

```
Raspberry Pi 4 Model B
    │
    ├─ I2C Bus (SDA/SCL)
    │   │
    │   └─ PCA9685 (Address: 0x40)
    │       │
    │       ├─ Channel 0 ──> ステアリングサーボ
    │       │
    │       ├─ Channel 1 ──┐
    │       │              ├─> Hブリッジドライバー (L298N/TB6612等)
    │       └─ Channel 2 ──┘      └─> DCモーター
    │
    └─ GPIO (XSHUT制御用、センサー用)
```

#### Raspberry Pi 4 と PCA9685 の接続

| Raspberry Pi 4 | PCA9685 | 説明 |
|----------------|---------|------|
| **Pin 1 (3.3V)** | VCC | 電源（3.3V、または外部5V） |
| **Pin 3 (GPIO2/SDA)** | SDA | I2Cデータ線 |
| **Pin 5 (GPIO3/SCL)** | SCL | I2Cクロック線 |
| **Pin 6 (GND)** | GND | グラウンド |
| **Pin 2 (5V)** または外部電源 | V+ | PCA9685のロジック電源（5V推奨） |

**注意**: PCA9685のV+（ロジック電源）は5Vが必要です。Raspberry PiのPin 2から供給するか、外部電源を使用してください。

#### PCA9685 のチャンネル配線

##### Channel 0: ステアリングサーボ

| PCA9685 | ステアリングサーボ | 説明 |
|---------|-------------------|------|
| **Channel 0 (PWM出力)** | 信号線（オレンジ/白） | PWM制御信号 |
| **V+ (5V)** | 電源線（赤） | サーボの電源（5V-6V） |
| **GND** | グラウンド（黒/茶） | 共通グラウンド |

**注意**: サーボの電源は、PCA9685のV+から供給するか、別途適切な電源（通常5V-6V）を用意してください。サーボの消費電流に注意してください。

##### Channel 1 & 2: DCモーター（Hブリッジドライバー経由）

**Hブリッジドライバー（L298NまたはTB6612FNG）を使用する場合:**

| PCA9685 | Hブリッジドライバー | DCモーター | 説明 |
|---------|-------------------|-----------|------|
| **Channel 1 (PWM出力)** | IN1 (またはPWMA) | - | モーター制御信号1 |
| **Channel 2 (PWM出力)** | IN2 (またはPWMB) | - | モーター制御信号2 |
| **V+ (5V)** | VCC | - | ロジック電源（5V） |
| **GND** | GND | - | 共通グラウンド |
| - | VM (またはVCC) | - | モーター電源（6V-12V、モーター仕様による） |
| - | OUT1 | モーター端子1 | モーター出力1 |
| - | OUT2 | モーター端子2 | モーター出力2 |

**L298Nの場合の接続例:**
- PCA9685 Channel 1 → L298N IN1
- PCA9685 Channel 2 → L298N IN2
- L298N OUT1 → DCモーター端子1
- L298N OUT2 → DCモーター端子2
- L298N VM → モーター用電源（6V-12V、モーター仕様に合わせる）
- L298N VCC → 5V（ロジック電源）
- L298N GND → グラウンド

**TB6612FNGの場合の接続例:**
- PCA9685 Channel 1 → TB6612 PWMA
- PCA9685 Channel 2 → TB6612 PWMB
- TB6612 AIN1 → GND（固定）
- TB6612 AIN2 → VCC（固定、または別のGPIOで制御）
- TB6612 OUT1 → DCモーター端子1
- TB6612 OUT2 → DCモーター端子2
- TB6612 VM → モーター用電源（2.5V-13.5V）
- TB6612 VCC → 5V（ロジック電源）
- TB6612 GND → グラウンド

**注意**: Hブリッジドライバーの種類によって接続方法が異なります。データシートを確認してください。

#### 電源接続の詳細

##### 電源の種類と接続先

1. **Raspberry Pi 4の電源**
   - 5V/3A USB-C電源アダプターを使用
   - Pin 1 (3.3V) と Pin 2 (5V) から供給可能

2. **PCA9685のロジック電源**
   - **推奨**: 外部5V電源（安定化電源）
   - または Raspberry Pi の Pin 2 (5V) から供給
   - 電流容量: 100mA程度

3. **ステアリングサーボの電源**
   - **推奨**: 別途5V-6V電源（サーボの仕様による）
   - または PCA9685のV+から供給（電流容量に注意）
   - 電流容量: サーボの仕様による（通常500mA-2A）

4. **DCモーターの電源**
   - **必須**: 別途6V-12V電源（モーターの仕様による）
   - HブリッジドライバーのVM端子に接続
   - 電流容量: モーターの仕様による（通常1A-3A以上）

##### 電源投入順序（推奨）

1. Raspberry Pi の電源を投入
2. PCA9685のロジック電源（5V）を投入
3. サーボの電源を投入
4. モーターの電源を投入
5. プログラムを実行

**重要**: モーターの電源は最後に投入し、プログラム終了時は最初に切断してください。

#### グラウンド（GND）の接続

**すべてのデバイスのGNDを共通接続してください:**
- Raspberry Pi の GND (Pin 6, 9, 14, 20, 25, 30, 34, 39など)
- PCA9685 の GND
- Hブリッジドライバー の GND
- サーボ の GND
- モーター電源 の GND（負極）

**注意**: GNDの共通接続は必須です。接続しないと動作不良や故障の原因になります。

### ソフトウェア要件

#### 必要なライブラリのインストール

```bash
# Raspberry Pi上で実行
pip install adafruit-circuitpython-pca9685
pip install adafruit-circuitpython-motor
pip install adafruit-blinka
```

または、`setup/requirements.txt`から一括インストール：

```bash
pip install -r setup/requirements.txt
```

#### I2Cの有効化

Raspberry PiでI2Cを有効化する必要があります：

```bash
sudo raspi-config
# Interface Options -> I2C -> Enable
```

I2Cデバイスの確認：

```bash
sudo i2cdetect -y 1
# PCA9685が0x40で表示されることを確認
```

#### 権限設定

**重要**: I2Cバスへのアクセスには通常`sudo`権限が必要です。または、ユーザーを`i2c`グループに追加：

```bash
sudo usermod -aG i2c $USER
# ログアウト・ログイン後に反映
```

## Basic Usage（基本的な使用方法）

### インポート

```python
from auto_car_if.actuation.motor_driver import CarDriver
```

### 初期化

#### コンテキストマネージャーを使用（推奨）

```python
with CarDriver() as driver:
    # ここで操作を行う
    driver.set_steering(0.0)  # 中央
    driver.set_throttle(0.5)  # 前進
    # 自動的にクリーンアップされる
```

#### 手動管理

```python
driver = CarDriver()
try:
    # 操作を行う
    pass
finally:
    driver.cleanup()  # 必ずクリーンアップ
```

### ステアリング操作

```python
# 中央位置
driver.set_steering(0.0)

# 左に切る（-1.0が左最大）
driver.set_steering(-0.5)  # 左に50%

# 右に切る（+1.0が右最大）
driver.set_steering(0.5)   # 右に50%

# 最大左
driver.set_steering(-1.0)

# 最大右
driver.set_steering(1.0)
```

**値の範囲**: `-1.0`（左最大）から`+1.0`（右最大）

### スロットル操作

```python
# 停止（コースティング）
driver.set_throttle(0.0)

# 前進（0.0から1.0まで）
driver.set_throttle(0.3)   # 微速前進
driver.set_throttle(0.5)   # 中速前進
driver.set_throttle(1.0)   # 最大前進

# 後退（-1.0から0.0まで）
driver.set_throttle(-0.3)  # 微速後退
driver.set_throttle(-0.5)  # 中速後退
driver.set_throttle(-1.0)  # 最大後退
```

**値の範囲**: `-1.0`（後退最大）から`+1.0`（前進最大）
- `0.0`: 停止（コースティング）
- `> 0.0`: 前進
- `< 0.0`: 後退

### 完全な使用例

```python
import time
from auto_car_if.actuation.motor_driver import CarDriver

def main():
    with CarDriver() as driver:
        # ステアリングテスト
        print("中央位置")
        driver.set_steering(0.0)
        time.sleep(1)
        
        print("左に切る")
        driver.set_steering(-0.5)
        time.sleep(1)
        
        print("右に切る")
        driver.set_steering(0.5)
        time.sleep(1)
        
        # スロットルテスト
        print("微速前進")
        driver.set_throttle(0.3)
        time.sleep(2)
        
        print("停止")
        driver.set_throttle(0.0)
        time.sleep(1)
        
        print("微速後退")
        driver.set_throttle(-0.3)
        time.sleep(2)
        
        print("停止")
        driver.set_throttle(0.0)
        # コンテキストマネージャーが自動的にクリーンアップ

if __name__ == "__main__":
    main()
```

## Safety Notes（安全に関する注意事項）

### ⚠️ 重要な安全事項

1. **必ずクリーンアップを実行**
   - プログラム終了時や例外発生時にも、必ず`cleanup()`を呼び出すか、コンテキストマネージャーを使用してください
   - モーターが停止しないまま終了すると、予期しない動作を引き起こす可能性があります

2. **電源投入順序**
   - 推奨順序：
     1. Raspberry Piの電源を投入
     2. PCA9685の電源を投入
     3. サーボ・モーターの電源を投入
     4. プログラムを実行

3. **緊急停止**
   - プログラム実行中に緊急停止が必要な場合：
     ```python
     driver.stop()  # 即座に停止
     driver.cleanup()  # リソースを解放
     ```
   - または、`Ctrl+C`でプログラムを中断する場合でも、`try-finally`で確実にクリーンアップしてください

4. **実機テスト前の確認事項**
   - PCA9685が正しく接続されているか（`i2cdetect`で確認）
   - サーボとモーターの電源が適切か
   - 車体が安全な場所にあるか
   - 緊急停止の準備ができているか

5. **キャリブレーション**
   - デフォルトのパルス幅（`STEER_CENTER_US`, `STEER_LEFT_US`, `STEER_RIGHT_US`）は実機に合わせて調整が必要な場合があります
   - サーボの実際の動作範囲に合わせて調整してください

### エラーハンドリングの例

```python
import logging
from auto_car_if.actuation.motor_driver import CarDriver

logging.basicConfig(level=logging.INFO)

driver = None
try:
    driver = CarDriver()
    driver.set_steering(0.0)
    driver.set_throttle(0.3)
    # 操作を続ける...
except RuntimeError as e:
    logging.error(f"CarDriver error: {e}")
except KeyboardInterrupt:
    logging.info("Interrupted by user")
finally:
    if driver is not None:
        driver.cleanup()
        logging.info("CarDriver cleaned up")
```

## トラブルシューティング

### PCA9685が見つからない

```
RuntimeError: CarDriver initialization failed: ...
```

**対処法**:
- I2Cが有効になっているか確認: `sudo raspi-config`
- I2Cデバイスを確認: `sudo i2cdetect -y 1`
- 配線を確認（SDA/SCLが正しく接続されているか）
- アドレスが正しいか確認（デフォルトは0x40）

### モーターが動かない

**確認事項**:
- Hブリッジドライバーの電源が供給されているか
- Channel 1と2の配線が正しいか
- `set_throttle()`の値が適切か（0.0以外の値を使用）

### サーボが動かない

**確認事項**:
- サーボの電源が供給されているか
- Channel 0の配線が正しいか
- パルス幅の設定がサーボの仕様に合っているか

## 関連ファイル

- `motor_driver.py`: CarDriverクラスの実装
- `test_car_driver.py`: 動作確認用のテストスクリプト
