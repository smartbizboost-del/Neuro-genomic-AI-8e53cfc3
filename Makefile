# Makefile for Neuro-Genomic AI

.PHONY: help install test lint format run build docker-up docker-down deploy

help:
	@echo "Available commands:"
	@echo "  install     Install dependencies"
	@echo "  test        Run tests"
	@echo "  lint        Run linter"
	@echo "  format      Format code"
	@echo "  run         Run development server"
	@echo "  build       Build Docker images"
	@echo "  docker-up   Start Docker Compose"
	@echo "  docker-down Stop Docker Compose"
	@echo "  deploy      Deploy to OCI"

install:
	pip install -r requirements/base.txt
	pip install -r requirements/dev.txt

test:
	pytest tests/ -v --cov=src --cov-report=term-missing

lint:
	flake8 src/ --count --max-complexity=10 --statistics
	mypy src/ --ignore-missing-imports

format:
	black src/ tests/
	isort src/ tests/

run:
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

run-dashboard:
	streamlit run src/dashboard/app.py

docker-build:
	docker build -f docker/Dockerfile.api -t neuro-api .
	docker build -f docker/Dockerfile.worker -t neuro-worker .
	docker build -f docker/Dockerfile.dashboard -t neuro-dashboard .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

deploy:
	cd infrastructure/terraform && terraform init && terraform apply -auto-approve
	kubectl apply -f infrastructure/kubernetes/

seed-db:
	python scripts/init_db.py

train-model:
	python scripts/train_model.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov