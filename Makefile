# Makefile (versão compatível com Windows/WSL/Git Bash)

SHELL := /usr/bin/env bash

.PHONY: up down submit status logs build

up:
	@echo ">>> Subindo infraestrutura..."
	docker compose up -d

status:
	@echo ">>> Verificando status dos serviços..."
	docker compose ps

down:
	@echo ">>> Derrubando containers..."
	docker compose down

submit:
	@echo ">>> Submetendo job Spark padrão..."
	docker compose exec spark-master spark-submit \
		--master spark://spark-master:7077 \
		--conf spark.jars.ivy=/tmp/.ivy2 \
		/opt/spark/jobs/enem_pipeline.py

submit-file:
	@echo ">>> Submetendo job com arquivo: $(FILE)"
	docker compose exec spark-master spark-submit --master spark://spark-master:7077 $(FILE)

logs:
	docker compose logs -f --tail=100

build:
	@echo ">>> Buildando imagem personalizada..."
	docker build -t enem-spark-job -f Dockerfile .