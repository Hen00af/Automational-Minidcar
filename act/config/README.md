# config パッケージ

ハードウェア設定とユーティリティ関数を提供するパッケージ。

## 構成

- `hardware.py` - PCA9685、ESC、サーボの設定定数
- `sensors.py` - VL53L0X距離センサーの設定定数
- `timing.py` - タイミング関連の設定定数
- `utils.py` - `set_us()`などのユーティリティ関数

## 使用方法

```python
from act.config import hardware, sensors, timing, set_us

# ハードウェア設定
frequency = hardware.pca9685.FREQUENCY
esc_channel = hardware.pca9685.CH_ESC
servo_center = hardware.servo.US_CENTER

# センサー設定
sensor_pins = sensors.vl53l0x.XSHUT_PINS

# タイミング設定
esc_wait = timing.esc_init.MAX_WAIT

# ユーティリティ関数
set_us(channel, 1500)  # 1500μsを設定
```

## 設計思想

- **型安全性**: `@dataclass(frozen=True)`と`Final`型ヒントで不変性を保証
- **カテゴリ分離**: 関連する設定をグループ化
- **IDE補完**: クラス構造によりIDEの補完が効く
