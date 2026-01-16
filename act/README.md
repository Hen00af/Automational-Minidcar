# act パッケージ構成（TOFセンサー版）

このディレクトリは、TOFセンサーを用いたミニカー自律走行システムの「インターフェース・制御中核」を担うパッケージです。左側の壁との距離を一定に保つ（左手法/Wall Following）アルゴリズムを主眼に置いています。

## ディレクトリ構造

カメラ関連（camera, frame）を削除し、センサー関連（sensors, distance）に置き換えました。

```text
act/
├── domain/              # ドメインモデル（型定義）
│   ├── __init__.py
│   ├── distance.py      # [New] DistanceData (Front, Left, Right)
│   ├── features.py      # WallFeatures, GapError
│   ├── command.py       # Command, DriveMode
│   └── actuation.py     # ActuationStatus, ActuationCalibration, Telemetry
├── interfaces/          # インターフェース定義
│   ├── __init__.py
│   └── protocols.py    # DistanceSensorModule, Perception, Decision, Actuation
├── sensors/             # [New] 物理センサー実装
│   ├── __init__.py
│   ├── tof_mock.py      # 開発用モック
│   └── tof_vl53l0x.py   # 実機用（VL53L0X等）
├── perception/          # 知覚モジュール実装
│   ├── __init__.py
│   └── wall_position.py # [New] 距離データから壁の位置関係を特定
├── decision/            # 判断モジュール実装
│   ├── __init__.py
│   └── wall_follow.py   # [New] 左壁沿いP/PD制御
├── actuation/           # 駆動モジュール実装
│   ├── __init__.py
│   ├── pwm.py          
│   └── mock.py
├── orchestrator/         # オーケストレーター
│   ├── __init__.py
│   └── orchestrator.py  # センサー→知覚→判断→駆動のループ
└── README.md
```

## サブディレクトリの役割

### `domain/`
ドメインモデル（型定義）を集約したディレクトリ。各モジュール間でやり取りするデータ構造を定義します。
- `distance.py`: TOFセンサーから取得した距離データの型定義
- `features.py`: 知覚モジュールが抽出した特徴量の型定義（壁との誤差、前方障害物有無など）
- `command.py`: 判断モジュールが生成する制御コマンドの型定義
- `actuation.py`: 駆動モジュールのキャリブレーションとテレメトリの型定義

### `interfaces/`
各モジュール間のインターフェース（プロトコル）を定義します。
- `protocols.py`: `DistanceSensorModule`, `Perception`, `Decision`, `Actuation` のプロトコル定義

### `sensors/`
TOFセンサー（距離センサー）の実装モジュール。
- `tof_mock.py`: 開発・テスト用のモック実装
- `tof_vl53l0x.py`: 実機用のVL53L0X等の実装

### `perception/`
距離データから特徴量を抽出する知覚モジュールの実装。
- `wall_position.py`: 距離データから壁の位置関係を特定する実装

### `decision/`
特徴量から操舵・速度を決定する判断モジュールの実装。
- `wall_follow.py`: 左壁沿い走行のP/PD制御による判断実装

### `actuation/`
コマンドを物理信号（PWM等）に変換・出力する駆動モジュールの実装。
- `pwm.py`: pigpioを使用したPWM制御実装
- `mock.py`: 開発・テスト用のモック実装

### `orchestrator/`
全モジュールを統合して実行するオーケストレーター。
- `orchestrator.py`: `Orchestrator` クラス（メインループ）
  - `run_once()`: 1サイクル分の処理
  - `run_loop()`: 連続実行ループ
  - `emergency_stop()`: 緊急停止

## 主な変更点の詳細

### 1. domain/ (データ定義の変更)

画像フレームの代わりに、3方向の距離データを定義します。

#### domain/distance.py (新規)

```python
from dataclasses import dataclass

@dataclass
class DistanceData:
    front_mm: float  # 前方距離 (mm)
    left_mm: float   # 左方距離 (mm)
    right_mm: float  # 右方距離 (mm)
    timestamp: float
```

#### domain/features.py (変更)

知覚の結果として、「壁との誤差」や「前方の障害物有無」を定義します。

```python
from dataclasses import dataclass

@dataclass
class WallFeatures:
    error_from_target: float  # 目標距離とのズレ（正なら離れすぎ、負なら近すぎ）
    is_front_blocked: bool    # 前方に壁があるか（右折・停止判断用）
    is_corner_left: bool      # 左に壁がなくなったか（左折判断用）
```

### 2. interfaces/ (プロトコルの変更)

カメラの代わりに距離センサー用のプロトコルを定義します。

#### interfaces/protocols.py

```python
from typing import Protocol
from act.domain.distance import DistanceData
from act.domain.features import WallFeatures
from act.domain.command import Command

class DistanceSensorModule(Protocol):
    def read(self) -> DistanceData:
        """3方向の距離を計測して返す"""
        ...

class Perception(Protocol):
    def analyze(self, data: DistanceData) -> WallFeatures:
        """生の距離データから状況（特徴量）を抽出する"""
        ...

class Decision(Protocol):
    def decide(self, features: WallFeatures) -> Command:
        """状況に基づいてハンドル・アクセルを決定する"""
        ...
```

### 3. perception/ (知覚ロジック)

生の距離データを扱いやすい形に変換します。例えば、センサーエラー（極端な外れ値）の除去や、目標値との差分計算をここで行います。

#### perception/wall_position.py

```python
class WallPositionPerception:
    def __init__(self, target_distance_mm: float = 200.0):
        self.target = target_distance_mm

    def analyze(self, data: DistanceData) -> WallFeatures:
        # 左壁との距離誤差（P制御の入力値になる）
        error = data.left_mm - self.target
        
        # 前方の壁判定 (例: 15cm以内なら壁あり)
        front_blocked = data.front_mm < 150.0
        
        return WallFeatures(
            error_from_target=error,
            is_front_blocked=front_blocked,
            is_corner_left=(data.left_mm > 1000) # 左が開放されたらコーナーかも
        )
```

### 4. decision/ (制御ロジック)

ここが「左壁沿い走行」の肝になります。

#### decision/wall_follow.py

```python
from act.domain.command import Command, DriveMode

class WallFollowDecision:
    def __init__(self, kp: float = 0.5):
        self.kp = kp  # Pゲイン

    def decide(self, features: WallFeatures) -> Command:
        # 1. 緊急回避：前に壁があったら止まる or 右旋回
        if features.is_front_blocked:
            return Command(mode=DriveMode.BRAKE, speed=0, steering=0)
            # または右折: return Command(mode=DriveMode.FORWARD, speed=20, steering=1.0)

        # 2. 壁沿い制御（P制御）
        # errorが正（壁から離れすぎ） -> 左に切りたい -> steeringをマイナス（またはプラス、機構による）
        # errorが負（壁に近すぎ） -> 右に切りたい
        
        # 例: ステアリング -1.0(左) ～ 1.0(右) とする場合
        # 離れすぎ(error > 0) -> 近づくために左(-1.0)へ
        steering = -(features.error_from_target * self.kp)
        
        # クランプ処理 (-1.0 ~ 1.0 に収める)
        steering = max(min(steering, 1.0), -1.0)

        return Command(
            mode=DriveMode.FORWARD,
            speed=50,  # 一定速度
            steering=steering
        )
```

### 5. orchestrator/ (実行ループ)

カメラではなくセンサーをトリガーにします。

#### orchestrator/orchestrator.py

```python
class Orchestrator:
    def __init__(self, sensor: DistanceSensorModule, perception, decision, actuation):
        self.sensor = sensor
        self.perception = perception
        self.decision = decision
        self.actuation = actuation

    def run_once(self):
        # 1. 計測 (Measure)
        distance_data = self.sensor.read()
        
        # 2. 知覚 (Perceive)
        features = self.perception.analyze(distance_data)
        
        # 3. 判断 (Decide)
        command = self.decision.decide(features)
        
        # 4. 実行 (Act)
        self.actuation.apply(command)
```

## 設計思想

### DDDライクな構成
- **ドメインモデル**: `domain/` ディレクトリに型定義を集約
- **インターフェース**: `interfaces/` ディレクトリにプロトコル定義
- **実装**: 各機能モジュール（`sensors/`, `perception/`, `decision/`, `actuation/`）に実装を分離
- **オーケストレーション**: `orchestrator/` ディレクトリに統合ロジックを配置

### モジュール間の結合
各モジュールは `domain/` の型定義と `interfaces/` のプロトコルにのみ依存し、実装の詳細には依存しません。これにより、各モジュールを独立して開発・テストできます。

## 使用例

```python
from act.orchestrator import Orchestrator
from act.sensors import TOFVL53L0X
from act.perception import WallPositionPerception
from act.decision import WallFollowDecision
from act.actuation import PWMActuation

# 各モジュールを初期化
sensor = TOFVL53L0X()
perception = WallPositionPerception(target_distance_mm=200.0)
decision = WallFollowDecision(kp=0.5)
actuation = PWMActuation()

# Orchestratorで統合実行
orchestrator = Orchestrator(sensor, perception, decision, actuation)
orchestrator.run_loop()
```

## 開発・運用のポイント

- **型定義の変更**: `domain/` ディレクトリ内のファイルを編集
- **新しい実装の追加**: 対応するモジュールディレクトリ（`sensors/`, `perception/` 等）に新しい実装ファイルを追加
- **インターフェースの拡張**: `interfaces/protocols.py` でプロトコルを定義・拡張
- **モック実装**: 開発・テスト時は各モジュールの `mock.py` を使用可能
