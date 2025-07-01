#!/bin/bash
# Aguarda o HDFS ficar disponível
echo "⏳ Aguardando o HDFS responder em hadoop-namenode:9000..."

until nc -z hadoop-namenode 9870; do
  echo "❌ HDFS ainda não está pronto..."
  sleep 5
done

echo "✅ HDFS pronto. Iniciando job Spark..."
