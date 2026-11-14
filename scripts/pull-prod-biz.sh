#!/usr/bin/env bash
# Pull business data from production into local Docker — never users/auth.
# Usage:
#   ./scripts/pull-prod-biz.sh           # pull only → data-exports/<stamp>/
#   ./scripts/pull-prod-biz.sh --load    # pull + load into local compose DB
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOST="${VEDEL_SSH_HOST:-fserver}"
REMOTE_DIR="${VEDEL_REMOTE_DIR:-/opt/sites/vedel-portal}"
STAMP="${VEDEL_EXPORT_STAMP:-$(date +%Y%m%d-%H%M)}"
OUT="$ROOT/data-exports/$STAMP"
LOAD=0
[[ "${1:-}" == "--load" ]] && LOAD=1

MODELS=(
  stock.Category
  stock.Product
  stock.StockMovement
  sales.Party
  sales.Sale
  sales.SaleLine
  sales.Payment
  sales.PaymentAllocation
  crew.CrewMember
  crew.CrewDocument
  service.Device
  service.Job
  service.JobLine
  service.JobSoldPack
  service.JobSoldUnit
  service.JobSoldUnitPhoto
  service.JobSoldUnitMaterial
  service.JobPhoto
)

echo "==> Export dir: $OUT"
mkdir -p "$OUT"
printf '%s\n' "${MODELS[@]}" > "$OUT/models.txt"

echo "==> dumpdata on $HOST (no accounts/auth/sessions)"
ssh -o BatchMode=yes -o ConnectTimeout=30 "$HOST" bash -s -- "$REMOTE_DIR" "${MODELS[*]}" <<'REMOTE'
set -euo pipefail
REMOTE_DIR="$1"
shift
# shellcheck disable=SC2086
MODELS="$*"
cd "$REMOTE_DIR"
# </dev/null: exec -T would otherwise eat the rest of this heredoc from stdin.
docker compose exec -T backend python manage.py dumpdata \
  --indent 2 \
  $MODELS \
  > /tmp/vedel-biz.json </dev/null
# media: compose mounts ./media → /app/media
if [ -d media ]; then
  tar -C . -czf /tmp/media-biz.tgz media || tar -C . --ignore-failed-read -czf /tmp/media-biz.tgz media
elif [ -d backend/media ]; then
  tar -C backend -czf /tmp/media-biz.tgz media
else
  docker compose exec -T backend sh -c 'cd /app && tar -czf /tmp/media-biz.tgz media' </dev/null
  docker compose cp backend:/tmp/media-biz.tgz /tmp/media-biz.tgz
fi
test -f /tmp/media-biz.tgz
ls -lh /tmp/vedel-biz.json /tmp/media-biz.tgz
REMOTE

echo "==> scp fixtures"
scp -o BatchMode=yes -o ConnectTimeout=30 \
  "$HOST:/tmp/vedel-biz.json" "$OUT/vedel-biz.json"
scp -o BatchMode=yes -o ConnectTimeout=30 \
  "$HOST:/tmp/media-biz.tgz" "$OUT/media-biz.tgz"
ssh -o BatchMode=yes "$HOST" 'rm -f /tmp/vedel-biz.json /tmp/media-biz.tgz'

python3 - <<PY
import json
from collections import Counter
from pathlib import Path
p = Path("$OUT/vedel-biz.json")
data = json.loads(p.read_text())
print("objects", len(data))
print("models", Counter(o["model"] for o in data).most_common())
PY

echo "==> Wrote $OUT"
echo "    vedel-biz.json  media-biz.tgz  models.txt"

if [[ "$LOAD" -eq 1 ]]; then
  echo "==> Loading into local Docker (users untouched)"
  "$ROOT/scripts/load-prod-biz.sh" "$OUT"
fi
