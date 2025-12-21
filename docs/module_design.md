## module design

以下にソフトウェアアーキテクチャとインターフェース定義を記載する。

目的は、ハードウェアやアルゴリズムの詳細に依存せず、以下の明確に分離されたモジュールとして設計し、段階的・安全に実装を進められる土台を作ることです。

1. カメラ入力
2. 知覚（Perception）
3. 判断（Decision）
4. 駆動（Actuation）

---

## 設計方針

- 段階的実装（イテレーション）  
  第1イテレーションでは設計をシンプルに保つ事とし、以下の事項は次段階で検討する。
  - 並列化・非同期化
  - Decisionの入力として現在の状態(走行速度、ステアリングの向き)を与える。
- ハード依存の隔離
  PWM/I2C/サーボ/ESC などの物理制御は Actuation に閉じ込め、  
  上位層は抽象的な数値（-1〜1, 0〜1）のみを扱う。

---

## モジュール構成

Camera Module → Perception → Decision → Actuation

- Camera Module  
  カメラデバイスから画像を取得し、正規化された `Frame` を生成する。
- Perception  
  画像から進行方向に関する観測量（例：`lateral_bias`）と信頼度を算出する。
- Decision
  観測結果に基づき、操舵・速度・モードを含む `Command` を決定する。
- Actuation  
  抽象的な `Command` を、実機用の物理信号（PWM等）に変換して適用する。

これらは オーケストレーターによって順序通りに接続されます。

---

## このコードに含まれるもの / 含まれないもの

### 含まれるもの

- 各モジュールの **データ構造（dataclass）**
- モジュール間の **インターフェース定義（Protocol）**
- 全体をつなぐ **処理フローの骨格**

### 含まれないもの

- 画像処理アルゴリズムの実装
- モーターやサーボを直接動かすコード
- 特定ハードウェアへの依存実装

---

## 想定する読み方

1. `types_*.py` で **データの意味と責務**を把握する
2. `protocols.py` で **モジュール間の契約**を確認する
3. `orchestrator_skeleton.py` で **全体の流れ**を理解する
4. 各モジュールを段階的に実装・差し替える

## アーキテクチャ/インターフェース構成

```py
# ============================
# auto_car_if/
#   types_common.py
#   types_frame.py
#   types_features.py
#   types_command.py
#   types_vehicle_state.py
#   types_actuation.py
#   protocols.py
#   orchestrator_skeleton.py
# ============================

# --------------------------------
# types_common.py
# --------------------------------
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Optional


# --------------------------------
# types_frame.py
# --------------------------------
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Protocol, runtime_checkable


class ColorSpace(str, Enum):
    RGB = "RGB"


class PixelFormat(str, Enum):
    UINT8 = "uint8"


@runtime_checkable
class ImageBuffer(Protocol):
    """
    Camera module -> Perception の '画像' 最小契約。
    実体は numpy / bytes / custom など何でもよいが、メタ情報と生データ参照ができること。
    """
    @property
    def width(self) -> int: ...
    @property
    def height(self) -> int: ...
    @property
    def channels(self) -> int: ...
    @property
    def pixel_format(self) -> PixelFormat: ...
    @property
    def color_space(self) -> ColorSpace: ...
    def as_bytes(self) -> bytes: ...


@dataclass(frozen=True)
class Frame:
    """
    Camera module -> Perception 入力（1フレーム）。
    - color_space は RGB 固定（前段で正規化する方針）
    """
    frame_id: int
    t_capture_sec: float
    image: ImageBuffer

    # 将来用（第1イテレーションでは未使用でOK）
    camera_id: Optional[str] = None
    exposure_us: Optional[int] = None
    gain: Optional[float] = None


# --------------------------------
# types_features.py
# --------------------------------
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Optional


class PerceptionStatus(str, Enum):
    OK = "OK"
    INSUFFICIENT_SIGNAL = "INSUFFICIENT_SIGNAL"
    INVALID_INPUT = "INVALID_INPUT"


@dataclass(frozen=True)
class Features:
    """
    Perception -> Decision 出力。

    Contract:
    - lateral_bias: [-1.0, +1.0]
        + : 左へ寄りたい（右側の圧迫が強い等）
        - : 右へ寄りたい（左側の圧迫が強い等）
    - quality: [0.0, 1.0]
        推定の信頼度（0は信用しない、1は高信頼）
    """
    frame_id: int
    t_capture_sec: float

    lateral_bias: float   # [-1, +1]
    quality: float        # [0, 1]

    # 任意：追加の数値観測（拡張用）
    signals: Optional[Mapping[str, float]] = None

    # 任意：デバッグ用（Decisionは参照しない方針）
    debug: Optional[Mapping[str, Any]] = None

    status: PerceptionStatus = PerceptionStatus.OK


# --------------------------------
# types_command.py
# --------------------------------
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class DriveMode(str, Enum):
    RUN = "RUN"
    SLOW = "SLOW"
    STOP = "STOP"


@dataclass(frozen=True)
class Command:
    """
    Decision -> Actuation 出力。

    Contract:
    - steer: [-1.0, +1.0]
        + : 左へ切る
        - : 右へ切る
    - throttle: [0.0, +1.0]（前進のみ）
    - STOP の場合、throttle == 0.0 を保証する（安全契約）
    """
    frame_id: int
    t_capture_sec: float

    steer: float          # [-1, +1]
    throttle: float       # [0, +1]
    mode: DriveMode

    reason: Optional[str] = None


# --------------------------------
# types_vehicle_state.py  (雛形：第1イテレーションでは未使用でOK)
# --------------------------------
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class VehicleState:
    """
    将来拡張用の状態（雛形）。
    例: 変化率制限、スムージング、PID、見失い継続の判断などに使える。
    """
    t_state_sec: float

    prev_steer: Optional[float] = None      # [-1, +1]
    prev_throttle: Optional[float] = None   # [0, +1]
    dt_sec: Optional[float] = None

    lost_count: Optional[int] = None


# --------------------------------
# types_actuation.py
# --------------------------------
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


@dataclass(frozen=True)
class ActuationCalibration:
    """
    Command(正規化値) -> 実機信号(PWM等)への写像ルール（定数/設定）。
    ※第1イテレーションでは値は仮でも、I/Fとして分離しておく。
    """
    # steering servo
    steer_center_us: int
    steer_left_us: int     # steer=+1.0
    steer_right_us: int    # steer=-1.0

    # throttle (ESC)
    throttle_stop_us: int
    throttle_max_us: int   # throttle=+1.0

    # optional limits (safety clamp)
    steer_limit: float = 1.0
    throttle_limit: float = 1.0


class ActuationStatus(str, Enum):
    OK = "OK"
    STOPPED = "STOPPED"
    DRIVER_ERROR = "DRIVER_ERROR"
    CALIBRATION_ERROR = "CALIBRATION_ERROR"


@dataclass(frozen=True)
class Telemetry:
    """
    Actuation の適用結果（ログ/デバッグ向け）。
    """
    frame_id: int
    t_capture_sec: float

    status: ActuationStatus
    applied_steer: Optional[float] = None
    applied_throttle: Optional[float] = None

    steer_pwm_us: Optional[int] = None
    throttle_pwm_us: Optional[int] = None

    message: Optional[str] = None


# --------------------------------
# protocols.py  (Cのprototype相当)
# --------------------------------
from __future__ import annotations

from typing import Iterator, Protocol

from types_frame import Frame
from types_features import Features
from types_command import Command
from types_actuation import ActuationCalibration, Telemetry


class CameraModule(Protocol):
    """
    Camera module external I/F:
    - 最新フレームを提供する責務（RGB固定などの正規化はここで行う方針）
    """
    def frames(self) -> Iterator[Frame]:
        ...


class Perception(Protocol):
    """Perception external I/F: Frame -> Features"""
    def process(self, frame: Frame) -> Features:
        ...


class Decision(Protocol):
    """Decision external I/F (第1イテレーション): Features -> Command"""
    def decide(self, features: Features) -> Command:
        ...


class Actuation(Protocol):
    """Actuation external I/F: Command -> Telemetry"""
    def configure(self, calib: ActuationCalibration) -> None:
        ...

    def apply(self, command: Command) -> Telemetry:
        ...

    def stop(self, reason: str) -> Telemetry:
        ...

    def close(self) -> None:
        ...


# --------------------------------
# orchestrator_skeleton.py  (run_once / run_loop の骨格：設計レベル)
# --------------------------------
from __future__ import annotations

from typing import Optional

from protocols import CameraModule, Perception, Decision, Actuation
from types_actuation import Telemetry
from types_command import Command, DriveMode


class Orchestrator:
    """
    全体をつなぐ役（レベル0単一ループ想定）。
    - 中身（アルゴリズム/ハード）を知らず、I/Fだけで接続する。
    """
    def __init__(self, camera: CameraModule, perception: Perception, decision: Decision, actuation: Actuation):
        self.camera = camera
        self.perception = perception
        self.decision = decision
        self.actuation = actuation

    def run_once(self, frame) -> Telemetry:
        """
        1フレーム分の処理（例外処理や安全停止ポリシーは必要に応じて追加）。
        """
        features = self.perception.process(frame)
        command = self.decision.decide(features)
        telemetry = self.actuation.apply(command)
        return telemetry

    def run_loop(self) -> None:
        """
        連続実行（第1イテレーションは単純に繰り返すだけ）。
        最新優先の高度化（古いフレーム破棄等）は次イテレーションで扱う。
        """
        for frame in self.camera.frames():
            _ = self.run_once(frame)

    def emergency_stop(self, reason: str = "emergency") -> Telemetry:
        """
        上位から明示停止できる入口（設計上の口）。
        """
        return self.actuation.stop(reason)

```
