# scripts/status.sh - Mostra status resumido

cat <<'EOF' > status.sh
#!/bin/bash

docker compose ps
EOF
chmod +x status.sh