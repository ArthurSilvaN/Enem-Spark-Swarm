#!/bin/bash
set -e

# Wait for HDFS
echo "Waiting for HDFS..."
until hdfs dfs -ls hdfs://hadoop-namenode:8020/ >/dev/null 2>&1; do
  sleep 5
done

# Create directories
hdfs dfs -mkdir -p /user/enem/{csv_raw,csv,parquet,resultados}

echo "Starting Spark job..."
spark-submit \
  --master spark://spark-master:7077 \
  --conf spark.hadoop.fs.defaultFS=hdfs://hadoop-namenode:8020 \
  /app/main.py