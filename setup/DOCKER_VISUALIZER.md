# Docker環境でのビジュアライザー実行ガイド

Docker環境でビジュアライザーを実行する方法を説明します。

## 前提条件

### macOSの場合

1. **XQuartzのインストール**
   ```bash
   brew install --cask xquartz
   ```
   または [XQuartz公式サイト](https://www.xquartz.org/)からダウンロード

2. **XQuartzの起動**
   - アプリケーション > ユーティリティ > XQuartz を起動
   - XQuartz > Preferences > Security で「Allow connections from network clients」にチェック

3. **X11転送の設定**
   ```bash
   # XQuartzを再起動
   xhost +localhost
   ```

### Linuxの場合

X11サーバーが既に動作しているはずです。必要に応じて：

```bash
# X11転送を許可
xhost +local:docker
```

## Docker環境のセットアップ

### 1. Dockerイメージの再ビルド

matplotlibとnumpyが追加されたので、イメージを再ビルドします：

```bash
cd setup
docker-compose build
```

### 2. コンテナの起動

```bash
# バックグラウンドで起動
docker-compose up -d

# コンテナ内のシェルに接続
docker-compose exec app bash
```

### 3. ビジュアライザーの実行

コンテナ内で：

```bash
# ビジュアライザーを実行
python3 -m auto_car_if.scripts.run_visualizer
```

またはMakefileを使用（ホストマシンから）：

```bash
make docker-visualize
```

## トラブルシューティング

### X11転送が機能しない場合

**エラー:**
```
Error: cannot open display: :0
```

**解決方法:**

1. **macOSの場合:**
   ```bash
   # XQuartzが起動しているか確認
   ps aux | grep XQuartz
   
   # X11転送を許可
   xhost +localhost
   
   # DISPLAY環境変数を設定
   export DISPLAY=host.docker.internal:0
   ```

2. **Linuxの場合:**
   ```bash
   # X11転送を許可
   xhost +local:docker
   
   # DISPLAY環境変数を確認
   echo $DISPLAY
   ```

### 画像ファイルとして保存する方法

X11転送が難しい場合は、ビジュアライザーを画像ファイル保存モードで実行することもできます（将来実装予定）。

## 注意事項

- Docker環境では、macOSのTkinterバックエンドは使用できません
- Linux環境では、X11転送またはVNCを使用する必要があります
- パフォーマンスは、ホストマシンで直接実行する場合より若干低下する可能性があります

