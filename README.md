# Automational-Minidcar

TOFセンサーを用いたミニカー自律走行システム

左側の壁との距離を一定に保つ（左手法/Wall Following）アルゴリズムを実装した自律走行システムです。

## 構成

- **`act/`**: 実機用パッケージ（Raspberry Piで動作）
- **`mock/`**: モック実装パッケージ（開発・テスト用、ハードウェア不要）

## クイックスタート

### モック実装でテスト

```bash
cd mock
make run
# または
python -m mock
```

### 実機で実行

```bash
cd act
make run
```

## 詳細

- `act/README.md`: 実機パッケージの詳細
- `mock/README.md`: モックパッケージの詳細
