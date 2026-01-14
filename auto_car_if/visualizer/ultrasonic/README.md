# Ultrasonic Sensor Visualizer

超音波センサーを使ったナビゲーションシステムの挙動をリアルタイムで可視化するツールです。

## 機能

以下の情報をリアルタイムで表示します：

1. **センサー読み取り値**
   - Front, Left, Right の3つのセンサーの距離値（cm）
   - 安全距離と危険距離のライン表示

2. **知覚モジュールの出力**
   - Lateral Bias（横方向のバイアス）
   - Quality（信頼度）
   - Status（状態）

3. **判断モジュールの出力**
   - Steer（ステアリング値）
   - Throttle（スロットル値）
   - Mode（走行モード）

4. **駆動モジュールの状態**
   - 適用されたステアリング・スロットル値
   - ステータス情報

## 使用方法

### 基本的な実行

```bash
python -m auto_car_if.scripts.run_visualizer
```

または

```bash
python -m auto_car_if.visualizer.ultrasonic.test_visualizer
```

### 必要なライブラリ

```bash
pip install matplotlib numpy
```

## 表示内容

### グラフ表示

- **センサー読み取り値グラフ**: 3つのセンサーの距離値の時系列グラフ
- **Lateral Biasグラフ**: 知覚モジュールが計算した横方向バイアスの時系列グラフ
- **Qualityグラフ**: 知覚モジュールの信頼度の時系列グラフ
- **Steer & Throttleグラフ**: 判断モジュールの出力値の時系列グラフ

### ステータスパネル

現在の状態をテキストで表示：
- センサー読み取り値（Front, Left, Right）
- 知覚モジュールの状態と出力値
- 判断モジュールの出力値
- 駆動モジュールの状態

## モックモードでのテスト

macOSやWindowsなどの開発環境では、自動的にモック実装が使用されます。
モックセンサーの距離値を変更してテストする場合は、`UltrasonicSensorArray`のモック実装を使用してください：

```python
from auto_car_if.sensor import UltrasonicSensorArray

sensors = UltrasonicSensorArray(...)

# モックモードの場合、距離値を設定可能
if hasattr(sensors, 'set_simulated_distance'):
    sensors.set_simulated_distance('front', 50.0)
    sensors.set_simulated_distance('left', 40.0)
    sensors.set_simulated_distance('right', 45.0)
```

## 停止方法

- matplotlibウィンドウを閉じる
- ターミナルで `Ctrl+C` を押す

## 注意事項

- リアルタイム更新のため、CPU使用率が高くなる場合があります
- グラフの更新間隔は `update_interval_ms` パラメータで調整可能です（デフォルト: 50ms）
- 履歴サイズは `history_size` パラメータで調整可能です（デフォルト: 100サンプル）

