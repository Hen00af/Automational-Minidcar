# Automational-Minidcar Project

自律走行ミニカーバトルに向けた、モジュール化設計に基づく制御ソフトウェア。

## 1. プロジェクトの思想

「ハードウェアがなくてもソフトウェアを開発できる」状態を目指します。
各モジュール（知覚・判断・駆動）をI/O（型）で切り離すことで、並行開発を可能にします。

## 1.1. 現在のプロジェクトでできること

このプロジェクトは以下の3つの機能を提供します：

### 1. ダミーデータを使用してのI/Oテスト
- **目的**: ハードウェアなしで開発・テストが可能
- **実装**: 
  - `camera/mock.py`: ダミーフレームを生成（macOS/Windowsで使用）
  - `actuation/mock.py`: ダミーPWM制御（実際のハードウェアなしで動作）
- **メリット**: OpenCV/pigpioなどのハード依存ライブラリが不要で、PC上でロジック開発が可能

### 2. 実機と連結するための部品
- **目的**: Raspberry Pi上で実際のハードウェアを制御
- **実装**:
  - `camera/pi.py`: Raspberry Pi Camera用の実装（OpenCV使用）
  - `actuation/pwm.py`: pigpioを使用したPWM制御実装（GPIO 13/14）
- **メリット**: 実機環境で即座に動作可能

### 3. 実際の処理ロジックの実装
- **実装済み**:
  - `perception/line.py`: ライン検出ロジック（OpenCV使用、OTSU閾値処理）
  - `decision/simple.py`: P制御による判断ロジック
  - `orchestrator/orchestrator.py`: 全体を統合するメインループ
- **メリット**: モック環境で開発したロジックが、そのまま実機でも動作

### 自動切り替え機能
プラットフォームを自動検出し、適切な実装を選択します：
- **macOS/Windows**: 自動的にモック実装を使用
- **Linux (Raspberry Pi)**: 自動的に実機実装を使用

同じコードで、開発環境ではモック、実機環境では実機が動作します。

## 2. ソフトウェアアーキテクチャ

```mermaid
flowchart LR
  CAM[Camera Module] -->|Frame| PER[Perception]
  PER -->|Features| DEC[Decision]
  DEC -->|Command| ACT[Actuation]
  ACT -->|Telemetry| LOG[Logger]
  
  US[超音波センサ] -.->|Distance| DEC
```

### モジュール構成

- **Camera**: 画像取得・正規化（RGB/リサイズ）
- **Perception**: 画像から「左右のズレ（lateral_bias）」を抽出
- **Decision**: ズレと距離から「ステアリング・スロットル」を決定
- **Actuation**: 抽象的な数値を物理的なPWM信号（実機制御）へ変換

## 3. インターフェース定義 (I/O)

各担当者は以下の「バトン」の形を守って実装してください。

### A. Frame (Camera → Perception)

```python
@dataclass(frozen=True)
class Frame:
    frame_id: int
    t_capture_sec: float
    image: ImageBuffer  # RGB画像データ（Protocolで抽象化）
```

### B. Features (Perception → Decision)

```python
@dataclass(frozen=True)
class Features:
    frame_id: int
    t_capture_sec: float
    lateral_bias: float  # [-1.0 (左寄り) 〜 +1.0 (右寄り)] ※0.0が中央
    quality: float       # [0.0 〜 1.0] (信頼度)
    status: PerceptionStatus  # OK / INSUFFICIENT_SIGNAL / INVALID_INPUT
```

### C. Command (Decision → Actuation)

```python
@dataclass(frozen=True)
class Command:
    frame_id: int
    t_capture_sec: float
    steer: float      # [-1.0 (右) 〜 +1.0 (左)]
    throttle: float   # [0.0 (停止) 〜 1.0 (最大)]
    mode: DriveMode   # RUN / SLOW / STOP
```

### D. Telemetry (Actuationからの出力)

```python
@dataclass(frozen=True)
class Telemetry:
    frame_id: int
    t_capture_sec: float
    status: ActuationStatus  # OK / STOPPED / DRIVER_ERROR
    applied_steer: Optional[float]
    applied_throttle: Optional[float]
    steer_pwm_us: Optional[int]
    throttle_pwm_us: Optional[int]
```

## 4. 実機仕様 (TOYOTAスライド準拠)

12/27までに「制御用ドライバ」を以下の物理仕様に適合させます。

| 項目 | 接続・制御方法 | 備考 (スライドPAGE 46-47参照) |
|------|----------------|-------------------------------|
| 駆動モータ | PWM (GPIO No.13) | 標準値: 380付近 |
| 操舵サーボ | PWM (GPIO No.14) | 標準値: 400付近 |
| 超音波センサ | TRIG / ECHO | 3.3V降圧回路を必須とする |
| 緊急停止 | ソフトウェア割り込み | 全PWM出力を即座にニュートラルへ |

## 5. 開発ロードマップ

### P1: 基盤確定 ✅ 完了
- **ゴール**: 制御用ドライバを実機に差し替え、前後左右が100%動く状態にする。
- **完了内容**: 
  - `Actuation.apply()` の中で実際のPWM制御を実装済み（`actuation/pwm.py`）
  - モック実装も用意済み（`actuation/mock.py`）
  - プラットフォーム自動検出による切り替え機能実装済み

### P2: 認識実装 ✅ 完了
- **ゴール**: 撮影済み動画（Mock Frame）を使って、家で判断ロジックを完成させる。
- **完了内容**:
  - OpenCVを用いたライン検出実装済み（`perception/line.py`）
  - P制御による判断ロジック実装済み（`decision/simple.py`）
  - モック環境でのテストが可能

### P3: 実走完走 🔄 進行中
- **ゴール**: TIBコースにて「3周連続完走（速度不問）」を達成。
- **TODO**: 現場の照明に合わせた閾値調整。

## 6. 実行方法 (Orchestrator)

### 基本的な使い方

```python
from auto_car_if.orchestrator import Orchestrator
from auto_car_if.camera import PiCameraCV  # 自動的にモック/実機を選択
from auto_car_if.perception import LinePerception
from auto_car_if.decision import SimpleDecision
from auto_car_if.actuation import PWMActuation  # 自動的にモック/実機を選択

# 各モジュールを初期化（プラットフォームに応じて自動的にモック/実機が選択される）
camera = PiCameraCV(width=320, height=240)
perception = LinePerception()
decision = SimpleDecision()
actuation = PWMActuation()

# Orchestratorを初期化して実行
orchestrator = Orchestrator(camera, perception, decision, actuation)
orchestrator.run_loop()
```

**注意**: `PiCameraCV` と `PWMActuation` は、実行環境に応じて自動的にモックまたは実機実装が選択されます：
- **macOS/Windows**: モック実装が自動選択（ハードウェア不要）
- **Linux (Raspberry Pi)**: 実機実装が自動選択（pigpio/OpenCV必要）

### テスト実行

#### Makefileを使用（推奨）

```bash
make test        # テストを実行
make run-mock    # モック環境で実行
make run         # 実機環境で実行（Raspberry Pi用）
make help        # すべてのコマンドを表示
```

#### 直接実行

```bash
python -m tests.test_orchestrator
```

モックモジュールを使用したテストが実行され、以下の流れが確認できます：
1. カメラからフレーム取得
2. 認識処理（lateral_bias抽出）
3. 判断処理（ステアリング/スロットル決定）
4. 制御適用（PWM信号生成）

## 7. プロジェクト構成

```
Automational-Minidcar/
├── Makefile                      # タスク自動化（makeコマンド用）
├── README.md                     # このファイル
├── regulation.md                 # 大会レギュレーション
├── auto_car_if/                  # メインパッケージ
│   ├── main.py                   # Orchestrator（メインループ）
│   ├── domain/                   # ドメインモデル（型定義）
│   │   ├── __init__.py
│   │   ├── frame.py              # Frame, ImageBuffer, ColorSpace, PixelFormat
│   │   ├── features.py           # Features, PerceptionStatus
│   │   ├── command.py            # Command, DriveMode
│   │   ├── vehicle_state.py      # VehicleState
│   │   └── actuation.py          # ActuationCalibration, Telemetry, ActuationStatus
│   ├── interfaces/               # インターフェース定義
│   │   └── protocols.py          # モジュール間のプロトコル定義
│   ├── camera/                   # 画像取得・正規化モジュール
│   │   ├── __init__.py
│   │   ├── pi.py                 # PiCameraCV実装（OpenCV）
│   │   └── mock.py               # モック実装
│   ├── perception/               # 特徴量抽出モジュール
│   │   ├── __init__.py
│   │   └── line.py               # LinePerception実装（ライン検出）
│   ├── decision/                 # 判断・制御ロジックモジュール
│   │   ├── __init__.py
│   │   └── simple.py             # SimpleDecision実装（P制御）
│   └── actuation/                # PWM信号生成・実機制御モジュール
│       ├── __init__.py
│       ├── pwm.py                # PWMActuation実装（pigpio）
│       └── mock.py                # モック実装
│   ├── scripts/                  # 実行スクリプト
│   │   ├── __init__.py
│   │   └── run.py                # 実機実行スクリプト（Pi Zero 2 W + pigpio）
│   └── tests/                    # テストスイート
│       ├── __init__.py
│       └── test_orchestrator.py  # Orchestratorテスト（モック環境）
├── docs/                         # ドキュメント
│   └── module_design.md          # モジュール設計詳細
├── setup/                        # Docker開発環境
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── requirements.txt
│   ├── .dockerignore
│   └── README.md                 # Docker環境セットアップガイド
```

### 実行方法

#### Makefileを使用（推奨）

```bash
# ヘルプを表示
make help

# テスト実行（モック環境）
make test

# モック環境で実行
make run-mock

# 実機環境で実行（Raspberry Pi用）
make run

# クリーンアップ
make clean

# Docker環境の操作
make docker-build    # Dockerイメージをビルド
make docker-up       # Dockerコンテナを起動
make docker-shell    # Dockerコンテナのシェルに接続
```

#### 直接実行

##### 1. 開発環境でのテスト実行（モック）
```bash
python -m auto_car_if.tests.test_orchestrator
```
モック環境でOrchestrator全体の流れを確認できます。OpenCV/pigpioは不要です。
- macOS/Windowsでは自動的にモック実装が使用されます
- ダミーフレームとダミーPWM制御で、ロジックの動作確認が可能です

##### 2. 実機環境での実行
```bash
# 前提条件：
# - Raspberry Pi Zero 2 W上で実行
# - pigpiod起動済み（sudo pigpiod）
# - 依存ライブラリがインストール済み（setup/requirements.txt参照）

python -m auto_car_if.scripts.run
```
実機用のカメラ・認識・判断・制御が統合されて動作します。
- Linux環境では自動的に実機実装が使用されます
- 同じコードで、モック環境で開発したロジックがそのまま実機でも動作します


© 2024-2025 Automational-Minidcar Team. Developed for 42 Tokyo Minidcar Battle.
