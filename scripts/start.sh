#!/bin/bash
# scripts/start.sh - Inicializa a infraestrutura local

set -e

echo "[INFO] Subindo containers com docker-compose..."
docker compose up -d

echo "[INFO] Aguardando containers iniciarem..."
sleep 10

echo "[INFO] Containers ativos:"
docker ps --format "table {{.Names}}	{{.Status}}	{{.Ports}}"

echo "[INFO] Acesse o Spark Master UI: http://localhost:8080"
echo "[INFO] Acesse o HDFS NameNode UI: http://localhost:9870"
echo "[INFO] Acesse o Jupyter Notebook: http://localhost:8888 (token via logs)"