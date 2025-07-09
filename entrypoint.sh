#!/bin/bash
set -e

echo "⏳ Aguardando o HDFS responder em hadoop-namenode:8020..."
until nc -z namenode 8020; do
  echo "❌ HDFS ainda não está pronto..."
  sleep 5
done

echo "✅ HDFS disponível. Executando comandos de configuração..."

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
