# mock パッケージ

モック実装パッケージ（開発・テスト用）

TOFセンサーを用いたミニカー自律走行システムのモック実装です。実機のハードウェアを使用せずに、ソフトウェアの動作をテスト・開発できます。

## 特徴

- **実機依存の排除**: 実機用ハードウェアライブラリを使用せず、純粋なPythonコードのみ
- **Strategyパターン**: 異なる状況（Situation）を切り替えてテスト可能
- **Dependency Injection**: コンポーネント間の依存関係を明確化
- **ベストプラクティス**: ロギング、エラーハンドリング、型ヒントなどを適切に実装
- **明確なエントリーポイント**: `python -m mock`で簡単に実行可能

## ディレクトリ構造

```text
mock/
├── __init__.py           # パッケージ初期化
├── __main__.py          # 実行エントリーポイント（python -m mock）
├── core/                # コアモジュール
│   ├── __init__.py
│   ├── exceptions.py    # カスタム例外クラス
│   └── utils.py         # ユーティリティ関数
├── sensors/             # センサーモジュール
│   ├── __init__.py
│   └── mock_sensor.py   # MockSensor クラス
├── actuation/           # アクチュエーターモジュール
│   ├── __init__.py
│   ├── mock_actuator.py # MockActuator クラス
│   └── mock_channel.py  # MockChannel クラス
├── situations/          # 状況（Situation）モジュール（Strategy Pattern）
│   ├── __init__.py
│   └── base.py          # BaseSituation, DefaultSituation
├── config/              # 設定・ユーティリティ
│   ├── __init__.py
│   ├── constants.py     # 定数定義
│   ├── hardware.py      # ハードウェア設定
│   ├── sensors.py       # センサー設定
│   ├── timing.py        # タイミング設定
│   └── utils.py         # ユーティリティ関数
├── domain/              # ドメインモデル（actパッケージから参照）
├── interfaces/          # インターフェース定義（actパッケージから参照）
├── orchestrator/        # オーケストレーター（actパッケージから参照）
├── perception/          # 知覚モジュール（actパッケージから参照）
├── decision/            # 判断モジュール（actパッケージから参照）
├── Makefile             # ビルド・実行用Makefile
└── README.md            # このファイル
```

## 主要コンポーネント

### `__main__.py`

実行エントリーポイント。`python -m mock`で実行されます。

- コンポーネントの初期化と設定
- オーケストレーターの実行
- エラーハンドリングとロギング設定

### `sensors/mock_sensor.py`

距離センサーのモック実装を定義します。

- **`MockSensor`**: 距離センサーのモック実装
  - `Situation`（状況）に基づいて距離データを生成
  - Dependency Injectionパターンを使用

### `actuation/mock_actuator.py` と `actuation/mock_channel.py`

アクチュエーターのモック実装を定義します。

- **`MockActuator`**: アクチュエーターのモック実装
  - 実際のハードウェア制御は行わず、ログ出力のみ
  - PWM制御のシミュレーション
- **`MockChannel`**: PWMチャンネルのモック実装

### `situations/base.py`

Strategyパターンを使用して、異なる状況を切り替えてテストできます。

- **`BaseSituation`**: 状況の基底クラス（抽象クラス）
  - `get_distances(time_elapsed: float) -> DistanceData`: 経過時間に基づいて距離データを取得
  - `get_elapsed_time() -> float`: 開始からの経過時間を取得
  - `reset() -> None`: 開始時刻をリセット
- **`DefaultSituation`**: デフォルトの状況（壁沿い走行シミュレーション）
  - 左側に壁がある想定で、時間経過で値が変化する動的なシミュレーション

### `config/constants.py`

モック実装で使用する定数を定義します。

- PWM制御関連の定数
- ロギング関連の定数
- デフォルトの距離設定
- デフォルトのキャリブレーション設定
- ループ設定

### `core/exceptions.py`

カスタム例外クラスを定義します。

- **`MockError`**: モック実装の基底例外クラス
- **`CalibrationError`**: キャリブレーション未設定エラー
- **`SituationError`**: Situation関連のエラー

### `core/utils.py`

共通で使用するユーティリティ関数を定義します。

- **`get_logger(name: str) -> logging.Logger`**: ロガーを取得（シングルトンパターン）
- **`clamp(value, min_value, max_value) -> float`**: 値を指定範囲内にクランプ
- **`linear_interpolate(...)`**: 線形補間を行う

## 実行方法

### 基本的な実行

```bash
# 最もシンプルな方法（推奨）
python -m mock

# Makefileを使用
make run
```

### 詳細ログ付きで実行

```bash
# --verboseオプションを使用
python -m mock --verbose

# または -v オプション
python -m mock -v
```

### Makefileコマンド

```bash
make help      # 利用可能なコマンドを表示
make run       # モック実装を実行（デフォルト）
make clean     # Pythonキャッシュファイルを削除
```

## 使用例

### 基本的な使用例

```python
from mock.sensors import MockSensor
from mock.actuation import MockActuator
from mock.situations.base import DefaultSituation
from mock.config.constants import (
    DEFAULT_LEFT_DISTANCE_MM,
    DEFAULT_FRONT_DISTANCE_MM,
    DEFAULT_RIGHT_DISTANCE_MM,
)
from act.orchestrator import Orchestrator
from act.perception import WallPositionPerception
from act.decision import WallFollowDecision
from act.domain.actuation import ActuationCalibration

# Situationを作成（デフォルトの状況：壁沿い走行）
situation = DefaultSituation(
    left_distance=DEFAULT_LEFT_DISTANCE_MM,
    front_distance=DEFAULT_FRONT_DISTANCE_MM,
    right_distance=DEFAULT_RIGHT_DISTANCE_MM
)

# MockSensorにSituationを注入（Dependency Injection）
sensor = MockSensor(situation=situation, verbose=False)

# その他のコンポーネントを初期化
perception = WallPositionPerception(target_distance_mm=200.0)
decision = WallFollowDecision(base_speed=0.5)
actuation = MockActuator(verbose=False)

# キャリブレーションを設定
calib = ActuationCalibration(
    steer_center_us=1500,
    steer_left_us=1300,
    steer_right_us=1700,
    throttle_stop_us=1500,
    throttle_max_us=1600
)
actuation.configure(calib)

# オーケストレーターを作成
orchestrator = Orchestrator(sensor, perception, decision, actuation)

# 実行
orchestrator.run_loop(loop_interval_sec=0.1, log_interval_sec=1.0)
```

### カスタムSituationの作成

新しい状況（例：前方に壁がある、カーブがある）をテストする場合は、`BaseSituation`を継承した新しいクラスを作成します。

```python
from mock.situations.base import BaseSituation
from act.domain.distance import DistanceData
import time

class WallAheadSituation(BaseSituation):
    """前方に壁がある状況"""
    
    def get_distances(self, time_elapsed: float) -> DistanceData:
        # 前方の距離を短く設定（壁がある）
        return DistanceData(
            front_mm=100.0,  # 前方に壁
            left_mm=200.0,
            right_mm=300.0,
            timestamp=time.time()
        )

# 使用
situation = WallAheadSituation()
sensor = MockSensor(situation=situation)
```

## データフロー

```
┌─────────────┐
│  Situation  │  経過時間に基づいて距離データを生成
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ MockSensor  │  DistanceData (front, left, right, timestamp)
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
│MockActuator │  Telemetry (status, applied_steer, applied_throttle, steer_pwm_us, throttle_pwm_us)
└─────────────┘
```

## 設計思想

### Strategyパターン

異なる状況（Situation）を切り替えてテストできるように、Strategyパターンを採用しています。

- `BaseSituation`: 状況の基底クラス（インターフェース）
- `DefaultSituation`: デフォルトの実装（壁沿い走行シミュレーション）
- 新しい状況を追加する場合は、`BaseSituation`を継承して`get_distances()`メソッドを実装するだけ

### Dependency Injection

コンポーネント間の依存関係を明確化するため、Dependency Injectionパターンを使用しています。

- `MockSensor`は`Situation`をコンストラクタで受け取る
- これにより、異なる`Situation`を簡単に切り替え可能

### ベストプラクティス

- **ロギング**: `logging`モジュールを使用（`print`文は使用しない）
- **エラーハンドリング**: カスタム例外クラスを使用
- **型ヒント**: すべての関数・メソッドに型ヒントを追加
- **定数の外部化**: マジックナンバーを定数ファイルに集約
- **ドキュメンテーション**: Googleスタイルのdocstringを使用
- **明確なエントリーポイント**: `__main__.py`を使用して`python -m mock`で実行可能

### ファイル構造の整理

エントリーポイントを明確にするため、以下の方針でファイルを整理しています：

- `mock/`直下には最小限のファイルのみ（`__init__.py`、`__main__.py`、`README.md`、`Makefile`）
- 共通機能は`core/`ディレクトリに集約
- 各機能モジュールは専用のディレクトリに配置

## 設定の変更

### デフォルト設定の変更

`config/constants.py`でデフォルト設定を変更できます。

```python
# デフォルトの距離設定（mm）
DEFAULT_LEFT_DISTANCE_MM: Final[float] = 200.0
DEFAULT_FRONT_DISTANCE_MM: Final[float] = 500.0
DEFAULT_RIGHT_DISTANCE_MM: Final[float] = 300.0

# デフォルトのキャリブレーション設定（μs）
DEFAULT_STEER_CENTER_US: Final[int] = 1500
DEFAULT_STEER_LEFT_US: Final[int] = 1300
DEFAULT_STEER_RIGHT_US: Final[int] = 1700
DEFAULT_THROTTLE_STOP_US: Final[int] = 1500
DEFAULT_THROTTLE_MAX_US: Final[int] = 1600
```

### Situationのパラメータ変更

`DefaultSituation`のクラス変数でシミュレーションのパラメータを変更できます。

```python
# situations/base.py内
LEFT_VARIATION_AMPLITUDE: float = 20.0  # 左側の変動幅（mm）
LEFT_VARIATION_FREQUENCY: float = 0.5    # 左側の変動周波数（Hz）
FRONT_VARIATION_AMPLITUDE: float = 50.0  # 前方の変動幅（mm）
FRONT_VARIATION_PERIOD: float = 4.0      # 前方の変動周期（秒）
RIGHT_VARIATION_AMPLITUDE: float = 30.0 # 右側の変動幅（mm）
RIGHT_VARIATION_FREQUENCY: float = 0.3   # 右側の変動周波数（Hz）
```

## トラブルシューティング

### モジュールが見つからない

```bash
# PYTHONPATHを設定
export PYTHONPATH=/path/to/project:$PYTHONPATH

# またはMakefileを使用（自動的に設定される）
make run
```

### ログが出力されない

`verbose=True`を設定するか、`--verbose`オプションを使用してください。

```bash
# コマンドラインから
python -m mock --verbose

# またはコード内で
sensor = MockSensor(situation=situation, verbose=True)
actuation = MockActuator(verbose=True)
```

### 新しいSituationを追加したい

`mock/situations/`ディレクトリに新しいファイルを作成し、`BaseSituation`を継承してください。

```python
from mock.situations.base import BaseSituation
from act.domain.distance import DistanceData

class MyCustomSituation(BaseSituation):
    def get_distances(self, time_elapsed: float) -> DistanceData:
        # カスタムロジックを実装
        pass
```

## 開発ガイドライン

### コードスタイル

- PEP 8に準拠
- 型ヒントを必ず記述
- docstringはGoogleスタイルを使用
- マジックナンバーは定数ファイルに定義

### テスト

新しい機能を追加する際は、以下を確認してください：

1. 型ヒントが正しく記述されているか
2. docstringが適切に記述されているか
3. エラーハンドリングが適切か
4. ロギングが適切に実装されているか

### 依存関係

このパッケージは`act`パッケージに依存しています。`act`パッケージの以下のモジュールを使用します：

- `act.domain.*`: ドメインモデル
- `act.interfaces.*`: インターフェース定義
- `act.orchestrator.*`: オーケストレーター
- `act.perception.*`: 知覚モジュール
- `act.decision.*`: 判断モジュール

## ライセンス

このパッケージはプロジェクトの一部として提供されます。
