# Makefile for Task Management API

.PHONY: install run test test-cov clean format lint

install:
	uv sync

run:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	uv run pytest tests/ -v

test-cov:
	uv run pytest tests/ --cov=app --cov-report=html

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

format:
	uv run black app/ tests/

lint:
	uv run flake8 app/ tests/