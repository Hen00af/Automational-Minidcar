# act パッケージ

TOFセンサーを用いたミニカー自律走行システムの「インターフェース・制御中核」を担うパッケージです。左側の壁との距離を一定に保つ（左手法/Wall Following）アルゴリズムを実装しています。

## ディレクトリ構造

```text
act/
├── domain/              # ドメインモデル（型定義）
│   ├── __init__.py
│   ├── distance.py      # DistanceData (Front, Left, Right)
│   ├── features.py      # WallFeatures, GapError
│   ├── command.py       # Command, DriveMode
│   └── actuation.py     # ActuationStatus, ActuationCalibration, Telemetry
├── interfaces/          # インターフェース定義
│   ├── __init__.py
│   └── protocols.py     # DistanceSensorModule, Perception, Decision, Actuation
├── config/              # 設定・ユーティリティ
│   ├── __init__.py
│   ├── hardware.py      # PCA9685、ESC、サーボの設定定数
│   ├── sensors.py       # VL53L0X距離センサーの設定定数
│   ├── timing.py        # タイミング関連の設定定数
│   ├── utils.py         # set_us()などのユーティリティ関数
│   └── README.md        # configパッケージの詳細説明
├── sensors/             # 物理センサー実装
│   ├── __init__.py
│   └── tof.py           # 実機用（TOFSensor - VL53L0X）
├── perception/          # 知覚モジュール実装
│   ├── __init__.py
│   └── wall_position.py # 距離データから壁の位置関係を特定
├── decision/            # 判断モジュール実装
│   ├── __init__.py
│   └── wall_follow.py   # 左壁沿いP制御
├── actuation/           # 駆動モジュール実装
│   ├── __init__.py
│   └── pwm.py           # pigpioを使用したPWM制御実装
├── orchestrator/        # オーケストレーター
│   ├── __init__.py
│   └── orchestrator.py  # センサー→知覚→判断→駆動のループ
├── run.py               # 実機実行スクリプト
├── Makefile             # ビルド・実行用Makefile
└── README.md            # このファイル
```

## サブディレクトリの役割

### `domain/`
ドメインモデル（型定義）を集約したディレクトリ。各モジュール間でやり取りするデータ構造を定義します。

- **`distance.py`**: TOFセンサーから取得した距離データの型定義
  - `DistanceData`: 前・左・右の距離データ（タイムスタンプ付き）
- **`features.py`**: 知覚モジュールが抽出した特徴量の型定義
  - `WallFeatures`: 壁との誤差、前方障害物有無、左コーナー判定など
- **`command.py`**: 判断モジュールが生成する制御コマンドの型定義
  - `Command`: ステアリング、スロットル、走行モード
  - `DriveMode`: RUN, SLOW, STOP
- **`actuation.py`**: 駆動モジュールのキャリブレーションとテレメトリの型定義
  - `ActuationCalibration`: PWM値への変換設定
  - `Telemetry`: 駆動結果のテレメトリ

### `interfaces/`
各モジュール間のインターフェース（プロトコル）を定義します。

- **`protocols.py`**: 以下のプロトコル定義
  - `DistanceSensorModule`: 距離センサーのインターフェース
  - `Perception`: 知覚モジュールのインターフェース
  - `Decision`: 判断モジュールのインターフェース
  - `Actuation`: 駆動モジュールのインターフェース

### `config/`
ハードウェア設定とユーティリティ関数を提供するパッケージ。

- **`hardware.py`**: PCA9685、ESC、サーボの設定定数
- **`sensors.py`**: VL53L0X距離センサーの設定定数
- **`timing.py`**: タイミング関連の設定定数
- **`utils.py`**: `set_us()`などのユーティリティ関数

詳細は `config/README.md` を参照してください。

### `sensors/`
TOFセンサー（距離センサー）の実装モジュール。

- **`tof.py`**: 実機用のVL53L0X実装（`TOFSensor`クラス）
  - 3つのVL53L0Xセンサー（前・左・右）をI2Cで制御
  - XSHUTピンを使用してI2Cアドレスを設定

### `perception/`
距離データから特徴量を抽出する知覚モジュールの実装。

- **`wall_position.py`**: `WallPositionPerception`クラス
  - 左壁との距離誤差を計算（目標距離からのズレ）
  - 前方の壁判定（閾値以内なら壁あり）
  - 左側のコーナー判定（距離が閾値以上なら壁がない）

### `decision/`
特徴量から操舵・速度を決定する判断モジュールの実装。

- **`wall_follow.py`**: `WallFollowDecision`クラス
  - 左壁沿い走行のP制御（比例制御）
  - 前方に壁がある場合：停止または右折
  - 左コーナーの場合：左折
  - 通常時：誤差に比例してステアリングを調整

### `actuation/`
コマンドを物理信号（PWM等）に変換・出力する駆動モジュールの実装。

- **`pwm.py`**: `PWMActuation`クラス
  - pigpioを使用したPWM制御実装
  - PCA9685を使用してESCとサーボを制御

### `orchestrator/`
全モジュールを統合して実行するオーケストレーター。

- **`orchestrator.py`**: `Orchestrator`クラス
  - `run_once()`: 1サイクル分の処理（計測→知覚→判断→実行）
  - `run_loop()`: 連続実行ループ（ループ間隔・ログ間隔を設定可能）
  - `emergency_stop()`: 緊急停止
  - `timing_log_path` にセンサー/駆動/ループの実測周波数（Hz）を出力

## 実行方法

### 実機モード（Raspberry Pi）

実機のハードウェアを使用して実行します。

```bash
# Makefileを使用
make run

# 直接実行
python3 run.py
```

### Makefileコマンド

```bash
make help      # 利用可能なコマンドを表示
make run       # 実機モードで実行
make clean     # Pythonキャッシュファイルを削除
```

## 使用例

### 基本的な使用例

```python
from act.orchestrator import Orchestrator
from act.sensors import TOFSensor
from act.perception import WallPositionPerception
from act.decision import WallFollowDecision
from act.actuation import PWMActuation

# 実機実装を使用
sensor = TOFSensor()
perception = WallPositionPerception(target_distance_mm=200.0)
decision = WallFollowDecision(kp=0.03, base_speed=0.5)
actuation = PWMActuation()

# Orchestratorで統合実行
orchestrator = Orchestrator(sensor, perception, decision, actuation)
try:
    orchestrator.run_loop()
except KeyboardInterrupt:
    print("\nStopped by user")
finally:
    actuation.close()
```

## データフロー

```
┌─────────────┐
│   Sensor    │  DistanceData (front, left, right, timestamp)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Perception  │  WallFeatures (error_from_target, is_front_blocked, is_corner_left)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Decision   │  Command (steer, throttle, mode, reason)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Actuation  │  Telemetry (status, applied_steer, applied_throttle, steer_pwm_us, throttle_pwm_us)
└─────────────┘
```

## 設計思想

### DDDライクな構成
- **ドメインモデル**: `domain/` ディレクトリに型定義を集約
- **インターフェース**: `interfaces/` ディレクトリにプロトコル定義
- **実装**: 各機能モジュール（`sensors/`, `perception/`, `decision/`, `actuation/`）に実装を分離
- **オーケストレーション**: `orchestrator/` ディレクトリに統合ロジックを配置

### モジュール間の結合
各モジュールは `domain/` の型定義と `interfaces/` のプロトコルにのみ依存し、実装の詳細には依存しません。これにより、各モジュールを独立して開発・テストできます。

## 開発・運用のポイント

### 型定義の変更
`domain/` ディレクトリ内のファイルを編集します。変更時は関連するモジュールへの影響を確認してください。

### 新しい実装の追加
対応するモジュールディレクトリ（`sensors/`, `perception/`, `decision/`, `actuation/`）に新しい実装ファイルを追加します。インターフェースプロトコルに適合するように実装してください。

### インターフェースの拡張
`interfaces/protocols.py` でプロトコルを定義・拡張します。既存の実装への影響を確認してください。

### 設定の変更
`config/` ディレクトリ内のファイルで設定を変更します。詳細は `config/README.md` を参照してください。

### パラメータ調整
- **知覚モジュール**: `WallPositionPerception` の `target_distance_mm`、`front_blocked_threshold_mm`、`corner_left_threshold_mm`
- **判断モジュール**: `WallFollowDecision` の `kp`（Pゲイン）、`base_speed`、各種閾値
- **駆動モジュール**: `ActuationCalibration` のPWM値設定

## トラブルシューティング

### 実機モードでセンサーが動作しない
- Raspberry Pi環境であることを確認してください
- I2Cが有効になっているか確認してください
- センサーの接続とXSHUTピンの設定を確認してください

### 制御が不安定
- Pゲイン（`kp`）を調整してください
- ループ間隔（`loop_interval_sec`）を調整してください
- センサーの読み取り値にノイズがないか確認してください
