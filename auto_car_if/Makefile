.PHONY: help test run clean install docker-build docker-up docker-down docker-shell docker-logs lint format

# デフォルトターゲット
.DEFAULT_GOAL := help

# プロジェクトルート（auto_car_ifの親ディレクトリ）
PROJECT_ROOT := $(shell dirname $(shell pwd))

# Python実行コマンド
PYTHON := python3
PYTHON_MODULE := python -m
PYTHONPATH := $(PROJECT_ROOT):$(PYTHONPATH)
export PYTHONPATH

# Docker関連
DOCKER_COMPOSE := docker compose
DOCKER_COMPOSE_FILE := $(PROJECT_ROOT)/setup/docker-compose.yml
DOCKER_IMAGE := minicar-dev

# プロジェクト情報
PROJECT_NAME := Automational-Minidcar

##@ ヘルプ

help: ## このヘルプメッセージを表示
	@echo "使用可能なコマンド:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

##@ テスト

test: ## テストを実行（モック環境）
	@echo "🧪 テストを実行中..."
	PYTHONPATH=$(PROJECT_ROOT) $(PYTHON_MODULE) auto_car_if.tests.test_orchestrator

test-verbose: ## 詳細出力でテストを実行
	@echo "🧪 詳細出力でテストを実行中..."
	PYTHONPATH=$(PROJECT_ROOT) $(PYTHON_MODULE) auto_car_if.tests.test_orchestrator -v

##@ 実行

run: ## 実機環境で実行（カメラベース、Raspberry Pi用）
	@echo "🚗 実機環境で実行中（カメラベース）..."
	@echo "⚠️  警告: 車輪を上げてから実行してください"
	PYTHONPATH=$(PROJECT_ROOT) $(PYTHON_MODULE) auto_car_if.scripts.run

run-sensor: ## 実機環境で実行（センサーベース、Raspberry Pi用）
	@echo "🚗 実機環境で実行中（センサーベース）..."
	@echo "⚠️  警告: 車輪を上げてから実行してください"
	PYTHONPATH=$(PROJECT_ROOT) $(PYTHON_MODULE) auto_car_if.scripts.run_sensor

run-mock: ## モック環境で実行（カメラベース、開発用）
	@echo "🔧 モック環境で実行中（カメラベース）..."
	PYTHONPATH=$(PROJECT_ROOT) $(PYTHON_MODULE) auto_car_if.tests.test_orchestrator

run-sensor-mock: ## モック環境で実行（センサーベース、開発用）
	@echo "🔧 モック環境で実行中（センサーベース）..."
	PYTHONPATH=$(PROJECT_ROOT) $(PYTHON_MODULE) auto_car_if.scripts.run_sensor

##@ クリーンアップ

clean: ## Pythonキャッシュとビルドファイルを削除
	@echo "🧹 クリーンアップ中..."
	find $(PROJECT_ROOT) -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find $(PROJECT_ROOT) -type f -name "*.pyc" -delete 2>/dev/null || true
	find $(PROJECT_ROOT) -type f -name "*.pyo" -delete 2>/dev/null || true
	find $(PROJECT_ROOT) -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	find $(PROJECT_ROOT) -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	@echo "✅ クリーンアップ完了"

clean-all: clean ## すべてのキャッシュとビルドファイルを削除（venv除く）
	@echo "🧹 完全クリーンアップ中..."
	rm -rf $(PROJECT_ROOT)/.mypy_cache 2>/dev/null || true
	rm -rf $(PROJECT_ROOT)/.ruff_cache 2>/dev/null || true
	@echo "✅ 完全クリーンアップ完了"

##@ インストール

install: ## 依存関係をインストール
	@echo "📦 依存関係をインストール中..."
	pip install -r $(PROJECT_ROOT)/setup/requirements.txt

install-dev: install ## 開発用依存関係もインストール
	@echo "📦 開発用依存関係をインストール中..."
	pip install -r $(PROJECT_ROOT)/setup/requirements.txt

##@ Docker

docker-build: ## Dockerイメージをビルド
	@if [ ! -f $(PROJECT_ROOT)/setup/Dockerfile ]; then \
		echo "❌ エラー: $(PROJECT_ROOT)/setup/Dockerfile が見つかりません"; \
		echo "   Dockerfileを作成するか、setup/README.mdを参照してください"; \
		exit 1; \
	fi
	@echo "🐳 Dockerイメージをビルド中..."
	cd $(PROJECT_ROOT)/setup && docker build -t $(DOCKER_IMAGE) .

docker-up: ## Dockerコンテナを起動
	@if [ ! -f $(PROJECT_ROOT)/setup/docker-compose.yml ]; then \
		echo "❌ エラー: $(PROJECT_ROOT)/setup/docker-compose.yml が見つかりません"; \
		echo "   Docker Composeファイルを作成するか、setup/README.mdを参照してください"; \
		exit 1; \
	fi
	@if [ ! -f $(PROJECT_ROOT)/setup/Dockerfile ]; then \
		echo "❌ エラー: $(PROJECT_ROOT)/setup/Dockerfile が見つかりません"; \
		echo "   まず 'make docker-build' を実行するか、Dockerfileを作成してください"; \
		exit 1; \
	fi
	@echo "🐳 Dockerコンテナを起動中..."
	cd $(PROJECT_ROOT)/setup && $(DOCKER_COMPOSE) up -d

docker-down: ## Dockerコンテナを停止
	@if [ ! -f $(PROJECT_ROOT)/setup/docker-compose.yml ]; then \
		echo "⚠️  警告: $(PROJECT_ROOT)/setup/docker-compose.yml が見つかりません。スキップします"; \
		exit 0; \
	fi
	@echo "🐳 Dockerコンテナを停止中..."
	cd $(PROJECT_ROOT)/setup && $(DOCKER_COMPOSE) down

docker-shell: ## Dockerコンテナのシェルに接続
	@if [ ! -f $(PROJECT_ROOT)/setup/docker-compose.yml ]; then \
		echo "❌ エラー: $(PROJECT_ROOT)/setup/docker-compose.yml が見つかりません"; \
		exit 1; \
	fi
	@echo "🐳 Dockerコンテナのシェルに接続中..."
	cd $(PROJECT_ROOT)/setup && $(DOCKER_COMPOSE) exec app bash

docker-logs: ## Dockerコンテナのログを表示
	@if [ ! -f $(PROJECT_ROOT)/setup/docker-compose.yml ]; then \
		echo "❌ エラー: $(PROJECT_ROOT)/setup/docker-compose.yml が見つかりません"; \
		exit 1; \
	fi
	@echo "🐳 Dockerコンテナのログを表示中..."
	cd $(PROJECT_ROOT)/setup && $(DOCKER_COMPOSE) logs -f

docker-restart: docker-down docker-up ## Dockerコンテナを再起動

docker-clean: docker-down ## Dockerコンテナとイメージを削除
	@echo "🐳 Dockerイメージを削除中..."
	cd $(PROJECT_ROOT)/setup && docker rmi $(DOCKER_IMAGE) 2>/dev/null || true

##@ 開発

lint: ## コードのリントチェック（将来実装）
	@echo "🔍 リントチェック（未実装）"
	@echo "TODO: ruff, mypy, pylintなどを追加"

format: ## コードのフォーマット（将来実装）
	@echo "✨ コードフォーマット（未実装）"
	@echo "TODO: black, ruff formatなどを追加"

check: lint test ## リントとテストを実行

##@ その他

info: ## プロジェクト情報を表示
	@echo "📋 プロジェクト情報:"
	@echo "  プロジェクト名: $(PROJECT_NAME)"
	@echo "  Python: $$($(PYTHON) --version 2>&1)"
	@echo "  作業ディレクトリ: $$(pwd)"
	@echo "  プロジェクトルート: $(PROJECT_ROOT)"

version: ## バージョン情報を表示
	@echo "バージョン情報（未実装）"
