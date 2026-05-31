.PHONY: install dev test lint docker-build docker-up docker-down init-local-configs

install:
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --tb=short

lint:
	ruff check app/ tests/

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

# Create a local config directory for development
init-local-configs:
	mkdir -p trino_configs_local/catalog
	cp .env.example .env
	@echo "Edit .env to set TRINO_CONFIG_DIR=./trino_configs_local"
	@echo "Done. Run: make dev"
