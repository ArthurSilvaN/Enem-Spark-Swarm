#!/bin/bash
# scripts/stop.sh - Para e remove os containers

cat <<'EOF' > stop.sh
#!/bin/bash

set -e

echo "[INFO] Parando e removendo containers..."
docker compose down
EOF
chmod +x stop.sh