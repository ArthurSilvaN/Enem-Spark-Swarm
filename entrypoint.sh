#!/bin/bash
set -e

echo "⏳ Aguardando o HDFS responder em hadoop-namenode:8020..."
until nc -z namenode 8020; do
  echo "❌ HDFS ainda não está pronto..."
  sleep 5
done

echo "✅ HDFS disponível. Preparando diretórios..."

# Criação das pastas
hdfs dfs -mkdir -p /user/enem/csv_raw
hdfs dfs -mkdir -p /user/enem/csv
hdfs dfs -mkdir -p /user/enem/parquet
hdfs dfs -mkdir -p /user/enem/resultados
hdfs dfs -mkdir -p /user/enem/csv_raw/2020
hdfs dfs -mkdir -p /user/enem/csv_raw/2021

# Permissões
hdfs dfs -chmod -R 777 /user/enem
hdfs dfs -chmod -R 777 /user/enem/csv_raw/2020
hdfs dfs -chmod -R 777 /user/enem/csv_raw/2021

hdfs dfs -chmod -R 777 /user/enem/csv_raw/2020
hdfs dfs -chmod -R 777 /user/enem/csv_raw/2021

# Limpeza de execuções anteriores (idempotente)
hdfs dfs -rm -r -f /user/enem/csv_raw/2020/MICRODADOS_ENEM_2020.csv || true
hdfs dfs -rm -r -f /user/enem/csv_raw/2021/MICRODADOS_ENEM_2021.csv || true
hdfs dfs -rm -r -f /user/enem/csv_raw/2023/MICRODADOS_ENEM_2023.csv || true

export HADOOP_USER_NAME=root

echo "🚀 Executando spark-submit"
/opt/bitnami/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --conf spark.driver.bindAddress=0.0.0.0 \
  --conf spark.network.timeout=600s \
  --conf spark.executor.heartbeatInterval=60s \
  --conf spark.python.worker.reuse=true \
  --conf spark.executorEnv.PYSPARK_PYTHON=python3 \
  --conf spark.executorEnv.HADOOP_USER_NAME=root \
  /opt/spark/jobs/main.py
