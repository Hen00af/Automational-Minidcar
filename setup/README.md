# Docker環境セットアップガイド

このディレクトリには、42 Tokyo主催「自動運転ミニカーバトル」向けのDocker開発環境を構築するためのファイルが含まれています。

## 目次

- [プロジェクト概要](#プロジェクト概要)
- [ファイル構成](#ファイル構成)
- [前提条件](#前提条件)
- [セットアップ手順](#セットアップ手順)
- [開発ワークフロー](#開発ワークフロー)
- [インストール済みパッケージ](#インストール済みパッケージ)
- [環境の特徴](#環境の特徴)
- [実機環境への移行](#実機環境への移行)
- [トラブルシューティング](#トラブルシューティング)
- [よくある質問（FAQ）](#よくある質問faq)
- [参考リソース](#参考リソース)

## プロジェクト概要

### ターゲットハードウェア

- **メインボード**: Raspberry Pi Zero 2 W（メモリ512MB）
- **使用言語**: Python 3.9
- **主要センサー**: 
  - 超音波センサー（HC-SR04など）- 距離測定用
  - カメラモジュールV2 - 壁認識・障害物検知用
- **アクチュエータ**: 
  - 駆動用モーター（ESC制御）
  - 操舵用サーボモーター（PWM制御）
- **PWM制御**: PWM分岐ケーブル経由でGPIOから直接ESCとサーボを制御（周期17ms/60Hz）

### 開発目標

- **走行ロジック**: 3周の周回タイムを競うための最適化
- **制御ロジック**: 障害物との距離に応じたPWM値（パルス幅）の計算
- **自律走行**: 超音波センサーとカメラによる環境認識と自動回避

## ファイル構成

```
setup/
├── Dockerfile              # Dockerイメージ定義
├── docker-compose.yml      # Docker Compose設定ファイル
├── requirements.txt       # Python依存パッケージ一覧
├── .dockerignore          # Dockerビルド時に除外するファイル
└── README.md              # このファイル
```

### 各ファイルの役割

- **Dockerfile**: Raspberry Pi Zero 2 W向けの最適化されたDockerイメージを定義
- **docker-compose.yml**: 開発環境の起動・管理を簡単にする設定ファイル
- **requirements.txt**: プロジェクトに必要なPythonパッケージのバージョン固定
- **.dockerignore**: ビルド時に不要なファイルを除外してビルド時間を短縮

## 前提条件

### 必要なソフトウェア

1. **Docker Desktop** (最新版推奨)
   - Windows: [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
   - Mac: [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)
   - Linux: Docker Engine と Docker Compose

2. **Git** (オプション、プロジェクトのクローンに必要)

### システム要件

- **メモリ**: 最低4GB、推奨8GB以上
- **ディスク容量**: 最低5GBの空き容量
- **OS**: Windows 10/11、macOS 10.15以降、Linux（Ubuntu 20.04以降、Debian 13 (trixie)以降推奨）

## セットアップ手順

### 1. Docker Desktopのインストールと起動

#### Windows/Mac

1. [Docker Desktop](https://www.docker.com/products/docker-desktop/)からダウンロード
2. インストール後、Docker Desktopを起動
3. システムトレイにDockerアイコンが表示されることを確認

#### Linux

```bash
# Ubuntu/Debianの場合
sudo apt-get update
sudo apt-get install docker.io docker-compose-plugin
sudo systemctl start docker
sudo systemctl enable docker

# ユーザーをdockerグループに追加（再ログインが必要）
sudo usermod -aG docker $USER
```

**注意**: Debian 13 (trixie) を使用している場合、`docker-compose-plugin`が利用できない場合は、`docker-compose`を個別にインストールするか、`docker compose`（プラグイン版）を使用してください。

### 2. プロジェクトの準備

```bash
# プロジェクトルートに移動
cd /path/to/Automational-Minidcar

# setupディレクトリに移動
cd setup
```

### 3. Dockerイメージのビルド

**初回ビルド（5-10分かかります）:**

```bash
docker build -t minicar-dev .
```

**ビルドの確認:**

```bash
docker images | grep minicar-dev
```

### 4. コンテナの起動

#### docker-composeを使用（推奨）

```bash
# バックグラウンドで起動
docker-compose up -d

# コンテナ内のシェルに接続
docker-compose exec app bash
```

#### 直接dockerコマンドを使用

```bash
# Windows (PowerShell)
docker run -it --rm --privileged -v ${PWD}/..:/home/pi/code minicar-dev

# Mac/Linux
docker run -it --rm --privileged -v $(pwd)/..:/home/pi/code minicar-dev
```

### 5. 動作確認

コンテナ内で以下を実行して環境が正しく構築されているか確認:

```bash
# Pythonバージョン確認
python3 --version

# インストール済みパッケージ確認
pip3 list

# 作業ディレクトリ確認
pwd  # /home/pi/code が表示されるはず
ls -la  # プロジェクトファイルが表示されるはず
```

## 開発ワークフロー

### 基本的な開発フロー

1. **コンテナの起動**
   ```bash
   cd setup
   docker-compose up -d
   ```

2. **コンテナ内で作業**
   ```bash
   docker-compose exec app bash
   ```

3. **コードの編集**
   - ホストマシンでエディタを使用してコードを編集
   - 変更は自動的にコンテナ内に反映されます（ボリュームマウント）

4. **コードの実行・テスト**
   ```bash
   # コンテナ内で実行
   python3 your_script.py
   ```

5. **作業終了時**
   ```bash
   # コンテナから退出
   exit

   # コンテナを停止（必要に応じて）
   docker-compose down
   ```

### ホットリロード開発

コードの変更は即座にコンテナ内に反映されるため、以下のような開発サイクルが可能です:

1. ホストマシンでコードを編集
2. コンテナ内で実行・テスト
3. エラーがあれば修正して再実行

### Gitの使用

コンテナ内でもGitを使用できますが、ホストマシンでGitを使用することを推奨します（エディタの統合機能が使えるため）。

## インストール済みパッケージ

### システムパッケージ

- `build-essential`: C/C++コンパイラとビルドツール
- `git`: バージョン管理システム
- `vim`, `nano`: テキストエディタ
- `libopencv-dev`, `python3-opencv`: OpenCVライブラリ（カメラ処理用）

### Pythonパッケージ

詳細は `requirements.txt` を参照してください。

#### GPIO制御

- **RPi.GPIO** (0.7.1): Raspberry PiのGPIOピン制御用の標準ライブラリ
- **pigpio** (1.78): より高精度なPWM制御用（周期17ms/60Hzのパルス生成）

#### 画像処理

- **opencv-python** (4.8.1.78): カメラモジュールV2の画像解析用
- **numpy** (1.24.3): 数値計算ライブラリ（OpenCVの依存関係）

#### その他

- **pyserial** (3.5): シリアル通信用（将来的な拡張用）

### パッケージの追加

新しいパッケージを追加する場合:

1. `requirements.txt`に追加
2. コンテナを再ビルド:
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

または、コンテナ内で直接インストール（一時的）:

```bash
pip3 install package-name
```

## 環境の特徴

### クロスプラットフォーム対応

#### Windows/Mac（シミュレーション環境）

- ✅ コードのロジック開発
- ✅ アルゴリズムのテスト
- ✅ デバッグ
- ❌ GPIOアクセス（エラーは出ますが無視可能）
- ❌ 実機ハードウェア制御

**用途**: 開発初期のロジック実装やテストに最適

#### Linux実機環境（Raspberry Pi）

- ✅ 完全なGPIO/I2Cアクセス
- ✅ 実機ハードウェア制御
- ✅ カメラモジュールアクセス
- ✅ 実際の走行テスト

**用途**: 実機での動作確認や最終調整

### 最適化

#### メモリ最適化

- **ベースイメージ**: `python:3.9-slim-bullseye`（軽量版）
- **パッケージ**: `--no-install-recommends`で最小限のインストール
- **イメージサイズ**: 約500MB（通常のpython:3.9より約60%削減）

#### ビルド最適化

- `.dockerignore`で不要なファイルを除外
- レイヤーキャッシュを活用した高速ビルド
- マルチステージビルドは使用せずシンプルに

## 実機環境への移行

### Linux実機環境（Raspberry Pi）での追加設定

実機環境でGPIO/I2Cアクセスが必要な場合は、`docker-compose.yml`を編集:

```yaml
services:
  app:
    # ... 他の設定 ...
    network_mode: host  # この行のコメントを外す
    volumes:
      - ../:/home/pi/code
      - /dev:/dev  # この行のコメントを外す
```

### 実機環境での注意点

1. **GPIOピン番号**: 実際のハードウェア構成に合わせて調整
2. **権限**: `privileged: true`が設定されていることを確認
3. **I2C有効化**: Raspberry PiでI2Cを有効化する必要がある場合があります
   ```bash
   sudo raspi-config
   # Interfacing Options > I2C > Enable
   ```

### 実機環境での直接実行（Dockerなし）

実機環境でDockerを使わずに直接実行する場合:

```bash
# 依存パッケージのインストール
pip3 install -r setup/requirements.txt

# プログラムの実行
python3 your_script.py
```

## トラブルシューティング

### Dockerデーモンが起動していない

**エラー:**
```
Cannot connect to the Docker daemon at unix:///.../docker.sock
```

**解決方法:**
1. Docker Desktopを起動
2. システムトレイにDockerアイコンが表示されているか確認
3. Docker Desktopの設定で「Start Docker Desktop when you log in」を有効化

### コンテナが起動しない

**確認事項:**
- Docker Desktopが起動しているか
- ポートが競合していないか（`docker ps -a`で確認）
- ディスク容量が十分か（`docker system df`で確認）
- メモリが不足していないか

**解決方法:**
```bash
# 停止中のコンテナを削除
docker container prune

# 未使用のイメージを削除
docker image prune

# システム全体のクリーンアップ
docker system prune
```

### ビルドが失敗する

**エラー:**
```
ERROR: failed to solve: ...
```

**解決方法:**
1. インターネット接続を確認
2. Dockerのプロキシ設定を確認
3. キャッシュをクリアして再ビルド:
   ```bash
   docker-compose build --no-cache
   ```

### Windows/MacでGPIOエラーが出る

**エラー:**
```
RuntimeError: This module can only be run on a Raspberry Pi!
```

**説明:**
これは正常な動作です。Windows/MacではGPIOアクセスはできませんが、コードのロジック開発には問題ありません。

**対処:**
- エラーを無視して開発を続行
- 実機環境（Raspberry Pi）で最終テストを実行

### ボリュームマウントが機能しない

**症状:** コンテナ内でファイルの変更が反映されない

**解決方法:**
1. パスの確認（Windowsでは`/c/Users/...`形式を使用）
2. Docker Desktopの設定で「File sharing」に該当ディレクトリが追加されているか確認
3. コンテナを再起動:
   ```bash
   docker-compose restart
   ```

### メモリ不足エラー

**エラー:**
```
ERROR: failed to start container: ...
```

**解決方法:**
1. Docker Desktopの設定でメモリ割り当てを増やす（推奨: 4GB以上）
2. 他のアプリケーションを閉じてメモリを確保
3. 不要なコンテナやイメージを削除

### パッケージのインストールエラー

**エラー:**
```
ERROR: Could not install packages due to an EnvironmentError
```

**解決方法:**
1. コンテナを再ビルド:
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```
2. パッケージのバージョンを確認（互換性の問題の可能性）

## よくある質問（FAQ）

### Q: コンテナを起動したままにしておいても大丈夫ですか？

A: はい、問題ありません。ただし、長時間使用しない場合は停止してリソースを節約することを推奨します。

### Q: ホストマシンとコンテナでファイルを共有できますか？

A: はい、`docker-compose.yml`で`../:/home/pi/code`としてマウントされているため、ホストマシンでの変更は自動的にコンテナ内に反映されます。

### Q: 複数のコンテナを同時に起動できますか？

A: 通常は1つのコンテナで十分です。複数起動する場合は、ポート番号やコンテナ名を変更する必要があります。

### Q: コンテナ内でGUIアプリケーションを使えますか？

A: X11フォワーディングの設定が必要です。通常は不要ですが、必要に応じて設定できます。

### Q: イメージサイズをさらに小さくできますか？

A: 可能ですが、機能が制限される可能性があります。現在の設定は機能性とサイズのバランスを考慮しています。

### Q: 実機環境でDockerを使う必要がありますか？

A: 必須ではありません。実機環境では直接実行することも可能です。Dockerは開発環境の統一に便利です。

### Q: パッケージのバージョンを変更したい

A: `requirements.txt`を編集してコンテナを再ビルドしてください。互換性に注意してください。

### Q: コンテナ内でGitを使えますか？

A: はい、Gitはインストールされています。ただし、ホストマシンでGitを使用することを推奨します。

## 参考リソース

### 公式ドキュメント

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)
- [RPi.GPIO Documentation](https://sourceforge.net/projects/raspberry-gpio-python/)

### 関連プロジェクト

- [42 Tokyo](https://42tokyo.jp/)
- [Raspberry Pi Zero 2 W](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/)

### コミュニティ

- [Raspberry Pi Forums](https://forums.raspberrypi.com/)
- [Stack Overflow - Docker](https://stackoverflow.com/questions/tagged/docker)
- [Stack Overflow - Raspberry Pi](https://stackoverflow.com/questions/tagged/raspberry-pi)

## サポート

問題が解決しない場合は、以下を確認してください:

1. このREADMEのトラブルシューティングセクション
2. Docker Desktopのログ
3. プロジェクトのIssue（GitHubを使用している場合）

---

**最終更新**: 2024年12月
