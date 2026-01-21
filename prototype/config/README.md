# config パッケージ

ハードウェア設定とユーティリティ関数を提供するパッケージ。

## 構成

- `hardware.py` - PCA9685、ESC、サーボの設定定数
- `sensors.py` - VL53L0X距離センサーの設定定数
- `timing.py` - タイミング関連の設定定数
- `perception.py` - 知覚モジュールの設定定数
- `decision.py` - 判断モジュールの設定定数
- `orchestrator.py` - オーケストレーターの設定定数
- `utils.py` - `set_us()`などのユーティリティ関数

## 使用方法

```python
from act.config import hardware, sensors, timing, perception, decision, orchestrator, set_us

# ハードウェア設定
frequency = hardware.pca9685.FREQUENCY
esc_channel = hardware.pca9685.CH_ESC
servo_center = hardware.servo.US_CENTER
pca9685_address = hardware.pca9685.I2C_ADDRESS

# センサー設定
sensor_pins = sensors.vl53l0x.XSHUT_PINS
sensor_addresses = sensors.vl53l0x.I2C_ADDRESSES

# タイミング設定
reset_wait = timing.sensor_init.RESET_WAIT

# 知覚モジュール設定
target_distance = perception.wall_position.TARGET_DISTANCE_MM
front_threshold = perception.wall_position.FRONT_BLOCKED_THRESHOLD_MM

# 判断モジュール設定
kp = decision.wall_follow.KP
base_speed = decision.wall_follow.BASE_SPEED

# オーケストレーター設定
loop_interval = orchestrator.LOOP_INTERVAL_SEC
log_interval = orchestrator.LOG_INTERVAL_SEC

# ユーティリティ関数
set_us(channel, 1500)  # 1500μsを設定
```

## 設計思想

- **型安全性**: `@dataclass(frozen=True)`と`Final`型ヒントで不変性を保証
- **カテゴリ分離**: 関連する設定をグループ化
- **IDE補完**: クラス構造によりIDEの補完が効く
