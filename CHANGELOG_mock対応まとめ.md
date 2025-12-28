# 最近の主な変更点まとめ（2025/12/28 時点）

## ディレクトリ・構造整理
- `auto_car_if/`配下を機能ごとにサブディレクトリ分割（camera, perception, decision, actuation）
- 型定義ファイル（types_*.py）のうち、actuation関連を `actuation/types_actuation.py` へ移動
- ルート直下の不要な.pyファイルを整理し、examples/testsディレクトリ新設

## importパス修正
- `types_actuation.py` の移動に伴い、全importパスを `from .types_actuation import ...` などに一括修正
- 他の型定義ファイルも今後、機能ごとに整理予定

## モック実装の追加
- macOSやWindows等、Raspberry Pi以外の環境でも開発・動作確認できるよう、以下のモックを追加
    - `camera/mock.py`: `PiCameraCV` のダミー実装（.frames()でダミーフレームを生成、.image/.frame_id/.t_capture_sec属性付き）
    - `actuation/mock.py`: `PWMActuation` のダミー実装（apply/stop/closeがエラーなく動作）
- `camera/__init__.py`/`actuation/__init__.py`で、Linux以外では自動的にモックを使うように分岐

## 実行・テストの流れ
- `examples/run_real.py` は、Raspberry Pi上では実機用、macOS等ではモックで動作可能
- モック環境ではOpenCV/pigpio等のハード依存ライブラリ不要
- テストやロジック開発をPC上で進め、最終的に実機で統合テストが可能

## その他
- README.mdやディレクトリ構成図も最新状態に追従
- 型定義と実装の論理的なまとまりを強化し、保守性・拡張性を向上

---

### 例：macOSでのrun_real.py実行時の流れ
1. `camera`/`actuation`は自動的にモックが使われる
2. Orchestratorの全体ループがエラーなく動作
3. perception/decision等のロジック開発・デバッグがPC上で可能

---

何か追加でまとめたい内容や、他の型定義整理の方針などあればご相談ください。
