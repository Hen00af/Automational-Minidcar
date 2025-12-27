# Automational-Minidcar

自律走行ミニカー用のソフトウェアアーキテクチャとインターフェース定義。

## 概要

ハードウェアやアルゴリズムの詳細に依存せず、明確に分離されたモジュールとして設計されています。

## モジュール構成

```
Camera → Perception → Decision → Actuation
```

1. **Camera Module**: カメラデバイスから画像を取得し、正規化された `Frame` を生成
2. **Perception**: 画像から進行方向に関する観測量（`lateral_bias`）と信頼度を算出
3. **Decision**: 観測結果に基づき、操舵・速度・モードを含む `Command` を決定
4. **Actuation**: 抽象的な `Command` を、実機用の物理信号（PWM等）に変換して適用

## エントリーポイント

`Orchestrator.run_loop()` がメインループとして実行の起点となります。

```python
from auto_car_if import Orchestrator

# 各モジュールの実装をインスタンス化
orchestrator = Orchestrator(camera, perception, decision, actuation)

# メインループを実行
orchestrator.run_loop()
```

## プロジェクト構造

```
auto_car_if/
  ├── types_frame.py          # Frame型定義
  ├── types_features.py       # Features型定義
  ├── types_command.py        # Command型定義
  ├── types_actuation.py      # Actuation関連型定義
  ├── types_vehicle_state.py  # VehicleState型定義（将来拡張用）
  ├── protocols.py            # 各モジュールのプロトコル定義
  └── orchestrator_skeleton.py # Orchestrator実装
```

## 詳細設計

詳細な設計仕様は `docs/module_design.md` を参照してください。

