# auto_car_if パッケージ構成

このディレクトリは、ミニカー自律走行システムの「インターフェース・制御中核」を担うパッケージです。
DDD（ドメイン駆動設計）ライクな構成で、型定義と実装を明確に分離しています。

## ディレクトリ構造

```text
auto_car_if/
├── domain/              # ドメインモデル（型定義）
│   ├── __init__.py
│   ├── frame.py         # Frame, ImageBuffer, ColorSpace, PixelFormat
│   ├── features.py      # Features, PerceptionStatus
│   ├── command.py       # Command, DriveMode
│   ├── vehicle_state.py # VehicleState
│   └── actuation.py     # ActuationCalibration, Telemetry, ActuationStatus
├── interfaces/          # インターフェース定義
│   └── protocols.py    # CameraModule, Perception, Decision, Actuation プロトコル
├── camera/              # カメラモジュール実装
│   ├── __init__.py
│   ├── pi.py           # PiCameraCV実装（OpenCV）
│   └── mock.py         # モック実装
├── perception/          # 知覚モジュール実装
│   ├── __init__.py
│   └── line.py         # LinePerception実装（ライン検出）
├── decision/            # 判断モジュール実装
│   ├── __init__.py
│   └── simple.py       # SimpleDecision実装（P制御）
├── actuation/           # 駆動モジュール実装
│   ├── __init__.py
│   ├── pwm.py          # PWMActuation実装（pigpio）
│   └── mock.py         # モック実装
├── orchestrator/         # Orchestrator（メインループ）
│   ├── __init__.py
│   └── orchestrator.py
├── scripts/              # 実行スクリプト
│   ├── __init__.py
│   └── run.py           # 実機実行スクリプト
└── tests/                # テストスイート
    ├── __init__.py
    └── test_orchestrator.py  # Orchestratorテスト
```

## サブディレクトリの役割

### `domain/`
ドメインモデル（型定義）を集約したディレクトリ。各モジュール間でやり取りするデータ構造を定義します。
- `frame.py`: カメラから取得した画像フレームの型定義
- `features.py`: 知覚モジュールが抽出した特徴量の型定義
- `command.py`: 判断モジュールが生成する制御コマンドの型定義
- `vehicle_state.py`: 車両状態の型定義（将来拡張用）
- `actuation.py`: 駆動モジュールのキャリブレーションとテレメトリの型定義

### `interfaces/`
各モジュール間のインターフェース（プロトコル）を定義します。
- `protocols.py`: `CameraModule`, `Perception`, `Decision`, `Actuation` のプロトコル定義

### `camera/`
カメラ画像取得・正規化モジュールの実装。
- `pi.py`: Raspberry Pi Camera用の実装（OpenCV使用）
- `mock.py`: 開発・テスト用のモック実装

### `perception/`
画像から特徴量を抽出する知覚モジュールの実装。
- `line.py`: ライン検出による知覚実装

### `decision/`
特徴量から操舵・速度を決定する判断モジュールの実装。
- `simple.py`: P制御による判断実装

### `actuation/`
コマンドを物理信号（PWM等）に変換・出力する駆動モジュールの実装。
- `pwm.py`: pigpioを使用したPWM制御実装
- `mock.py`: 開発・テスト用のモック実装

### `orchestrator/`
全モジュールを統合して実行するオーケストレーター。
- `orchestrator.py`: `Orchestrator` クラス（メインループ）
  - `run_once()`: 1フレーム分の処理
  - `run_loop()`: 連続実行ループ
  - `emergency_stop()`: 緊急停止

### `scripts/`
実行用スクリプト。
- `run.py`: 実機環境での実行スクリプト（Raspberry Pi用）

### `tests/`
テストスイート。
- `test_orchestrator.py`: Orchestratorの統合テスト（モック環境）

## ルート直下の主なファイル

- `orchestrator/`: 全モジュールをつなぐ `Orchestrator` クラス（メインループ）
- `__init__.py`: パッケージ初期化・主要クラスのエクスポート

## 設計思想

### DDDライクな構成
- **ドメインモデル**: `domain/` ディレクトリに型定義を集約
- **インターフェース**: `interfaces/` ディレクトリにプロトコル定義
- **実装**: 各機能モジュール（`camera/`, `perception/`, `decision/`, `actuation/`）に実装を分離
- **オーケストレーション**: `orchestrator/` ディレクトリに統合ロジックを配置

### モジュール間の結合
各モジュールは `domain/` の型定義と `interfaces/` のプロトコルにのみ依存し、
実装の詳細には依存しません。これにより、各モジュールを独立して開発・テストできます。

## 使用例

```python
from auto_car_if.orchestrator import Orchestrator
from auto_car_if.camera import PiCameraCV
from auto_car_if.perception import LinePerception
from auto_car_if.decision import SimpleDecision
from auto_car_if.actuation import PWMActuation

# 各モジュールを初期化
camera = PiCameraCV(width=320, height=240)
perception = LinePerception()
decision = SimpleDecision()
actuation = PWMActuation()

# Orchestratorで統合実行
orchestrator = Orchestrator(camera, perception, decision, actuation)
orchestrator.run_loop()
```

## 開発・運用のポイント

- **型定義の変更**: `domain/` ディレクトリ内のファイルを編集
- **新しい実装の追加**: 対応するモジュールディレクトリ（`camera/`, `perception/` 等）に新しい実装ファイルを追加
- **インターフェースの拡張**: `interfaces/protocols.py` でプロトコルを定義・拡張
- **モック実装**: 開発・テスト時は各モジュールの `mock.py` を使用可能
