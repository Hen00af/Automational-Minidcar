# 自動運転ミニカーバトル 開発環境

42 Tokyo主催「自動運転ミニカーバトル」向けの開発・シミュレーション環境です。

## プロジェクト概要

Raspberry Pi Zero 2 W を搭載したミニカーを制御し、Pythonプログラムによって超音波センサーやカメラの情報を解析、走行を自律化させることを目的としています。

## ターゲットハードウェア

- **メインボード**: Raspberry Pi Zero 2 W（メモリ512MB）
- **使用言語**: Python 3.x
- **主要センサー**: 超音波センサー（距離測定用）、カメラモジュールV2（壁認識用）
- **アクチュエータ**: 駆動用モーター（ESC）、操舵用サーボモーター（PWM制御）
- **PWM制御**: PWM分岐ケーブル経由でGPIOから直接ESCとサーボを制御（周期17ms/60Hz）

## 必須ライブラリ

- `RPi.GPIO`: Raspberry PiのGPIOピン制御用
- `pigpio`: より高精度なPWM制御用（周期17ms/60Hzのパルス生成）
- `opencv-python`: カメラモジュールV2の画像解析用（壁認識・自律走行）

## ディレクトリ構造

```
/home/pi/code/              # 作業ディレクトリ
├── togikai_function/       # カスタム関数モジュール
│   ├── __init__.py
│   ├── motor_control.py    # モーター制御関数
│   └── ultrasonic_sensor.py # 超音波センサー関数
└── 02_togikai_sample.py    # ベースコード（壁検知・回避走行）
```

## セットアップ

### Docker環境の構築

1. Dockerイメージのビルド:
```bash
docker build -t minicar-dev .
```

2. コンテナの起動:
```bash
docker run -it --rm --privileged minicar-dev
```

または、docker-composeを使用する場合:
```bash
docker-compose up -d
docker-compose exec app bash
```

### 実機環境での実行

1. 必要なライブラリのインストール:
```bash
pip3 install -r requirements.txt
```

2. プログラムの実行:
```bash
python3 02_togikai_sample.py
```

## 使用方法

### ベースコードの実行

```bash
# デフォルト（60秒間走行）
python3 02_togikai_sample.py

# カスタム時間で走行（例: 120秒）
python3 02_togikai_sample.py 120
```

### カスタム関数の使用例

```python
from togikai_function.motor_control import MotorController
from togikai_function.ultrasonic_sensor import UltrasonicSensor

# モーターコントローラーの初期化（GPIO直接制御）
# デフォルト: ステアリング=GPIO18, モーター=GPIO19
motor = MotorController(steering_pin=18, motor_pin=19)

# ステアリング角度を設定（-90度から90度）
motor.set_steering_angle(45)  # 右に45度

# モーター速度を設定（-100から100、0がニュートラル）
motor.set_motor_speed(50)  # 前進、速度50%

# 超音波センサーの初期化
ultrasonic = UltrasonicSensor(trigger_pin=23, echo_pin=24)

# 距離を測定
distance = ultrasonic.measure_distance()
print(f"距離: {distance} cm")

# クリーンアップ（重要: プログラム終了前に必ず実行）
motor.cleanup()
ultrasonic.cleanup()
```

## 開発のゴール

- **走行ロジック**: 3周の周回タイムを競うための最適化
- **制御ロジック**: 障害物との距離に応じたPWM値（パルス幅）の計算
  - ステアリング中央（0度）時のパルス幅調整
  - 前進・停止・後進の電流制御

## 注意事項

- **Pi Zero 2 Wのメモリ制約**: 512MBのメモリ制約を考慮し、Dockerfileはslim-bullseyeベースで最適化されています
- **PWM制御**: GPIOから直接ESCとサーボを制御します。周期17ms（60Hz）のPWMパルスを生成します
- **GPIOピン番号**: 実際のハードウェア構成に合わせて調整してください（デフォルト: ステアリング=GPIO18, モーター=GPIO19）
- **実機環境**: 実機環境でない場合、GPIO関連のエラーが表示されることがありますが、シミュレーション環境では無視できます
- **クリーンアップ**: プログラム終了前に必ず`motor.cleanup()`を呼び出してリソースを解放してください

## レギュレーション

詳細は `regulation.md` を参照してください。

## ライセンス

このプロジェクトは42 Tokyoの自動運転ミニカーバトル向けに作成されています。

