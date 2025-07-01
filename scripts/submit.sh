# scripts/submit.sh - Submete um job Spark do container

cat <<'EOF' > submit.sh
#!/bin/bash

APP_PATH=${1:-/opt/spark/jobs/main.py}

echo "[INFO] Submetendo job Spark: $APP_PATH"
docker compose exec spark-master spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  $APP_PATH
EOF
chmod +x submit.sh