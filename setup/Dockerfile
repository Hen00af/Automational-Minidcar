# Raspberry Pi Zero 2 W シミュレーション環境用 Dockerfile
# 42 Tokyo 自動運転ミニカーバトル向け開発環境
# メモリ512MB制約を考慮してslim-bullseyeベースに最適化

FROM python:3.9-slim-bullseye

# 作業ユーザーを作成（piユーザーとして実行）
RUN useradd -m -s /bin/bash pi && \
    echo "pi:raspberry" | chpasswd

# システムパッケージのインストール
# Pi Zero 2 Wのメモリ制約を考慮して最小限のパッケージのみインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    vim \
    nano \
    libopencv-dev \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの作成
RUN mkdir -p /home/pi/code/togikai_function && \
    chown -R pi:pi /home/pi

# 作業ディレクトリに移動
WORKDIR /home/pi/code

# Pythonパッケージのインストール
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

# piユーザーに切り替え
USER pi

# デフォルトコマンド
CMD ["/bin/bash"]

