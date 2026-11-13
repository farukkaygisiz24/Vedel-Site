#!/usr/bin/env bash
# Load a data-exports/<stamp> biz dump into local Docker. Never touches users/auth.
# Usage: ./scripts/load-prod-biz.sh [data-exports/STAMP]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${1:-}"
if [[ -z "$SRC" ]]; then
  SRC="$(ls -1d "$ROOT"/data-exports/*/ 2>/dev/null | sort | tail -1 || true)"
fi
SRC="${SRC%/}"
[[ -n "$SRC" && -f "$SRC/vedel-biz.json" ]] || {
  echo "No fixture: pass data-exports/<stamp> or pull first." >&2
  exit 1
}

cd "$ROOT"
docker compose ps --format '{{.Name}} {{.Status}}' | grep -q backend || docker compose up -d
for i in $(seq 1 30); do
  b=$(docker inspect -f '{{.State.Health.Status}}' vedel-site-main-backend-1 2>/dev/null || echo starting)
  [[ "$b" = "healthy" ]] && break
  sleep 2
done

echo "==> Remap user FKs → local users (fallback admin/first)"
python3 - <<PY
import json
from pathlib import Path

src = Path("$SRC/vedel-biz.json")
dst = Path("$SRC/vedel-biz.local.json")
data = json.loads(src.read_text())

# Discover local user ids via docker
import subprocess
raw = subprocess.check_output(
    [
        "docker", "compose", "exec", "-T", "backend",
        "python", "manage.py", "shell", "-c",
        "from accounts.models import Customer; "
        "print('IDS=' + ','.join(str(u.id) for u in Customer.objects.order_by('id')))",
    ],
    cwd="$ROOT",
    text=True,
)
local_ids = set()
for line in raw.splitlines():
    line = line.strip()
    if line.startswith("IDS="):
        local_ids = {int(x) for x in line[4:].split(",") if x.isdigit()}
        break
fallback = min(local_ids) if local_ids else 1
print("local_user_ids", sorted(local_ids), "fallback", fallback)
if not local_ids:
    raise SystemExit("No local users found — create/login users first, then reload.")

USER_FIELDS = {
    "created_by", "updated_by", "submitted_by", "user",
}
# natural-foreign may emit ["username"] lists — keep as-is if list/str
mapped = 0
nulled_user = 0
for o in data:
    f = o.get("fields") or {}
    for k in list(f):
        if k not in USER_FIELDS:
            continue
        v = f[k]
        if v is None:
            continue
        # natural key: ["username"] or username string from --natural-foreign
        if isinstance(v, list):
            # leave username natural keys; Django resolves on load
            continue
        if isinstance(v, str) and not v.isdigit():
            continue
        try:
            uid = int(v)
        except (TypeError, ValueError):
            continue
        if uid in local_ids:
            continue
        if k == "user":
            # CrewMember.user OneToOne — do not invent a login link
            f[k] = None
            nulled_user += 1
        else:
            f[k] = fallback
            mapped += 1

dst.write_text(json.dumps(data, ensure_ascii=False))
print("wrote", dst, "remapped", mapped, "nulled_crew_user", nulled_user)
PY

echo "==> Clear biz tables (users kept)"
docker compose exec -T backend python manage.py shell -c "
from django.apps import apps
from django.db import transaction
order = [
 'service.JobSoldUnitMaterial','service.JobSoldUnitPhoto','service.JobSoldUnit','service.JobSoldPack',
 'service.JobLine','service.JobPhoto','service.Job','service.Device',
 'sales.PaymentAllocation','sales.Payment','sales.SaleLine','sales.Sale','sales.Party',
 'stock.StockMovement','stock.Product','stock.Category',
 'crew.CrewDocument','crew.CrewMember',
]
with transaction.atomic():
  for label in order:
    m = apps.get_model(label)
    n = m.objects.all().delete()
    print('cleared', label, n)
"

echo "==> loaddata"
docker compose cp "$SRC/vedel-biz.local.json" backend:/tmp/vedel-biz.local.json
docker compose exec -T backend python manage.py loaddata /tmp/vedel-biz.local.json

echo "==> media"
mkdir -p "$ROOT/media" "$ROOT/backend/media"
tar -xzf "$SRC/media-biz.tgz" -C "$ROOT/media" 2>/dev/null || true
# tarball may contain media/ prefix or flat
if [[ -d "$ROOT/media/media" ]]; then
  rsync -a "$ROOT/media/media/" "$ROOT/media/" && rm -rf "$ROOT/media/media"
fi
# compose often serves from backend/media — mirror
rsync -a "$ROOT/media/" "$ROOT/backend/media/" 2>/dev/null || true
# if tarball extracted into backend-relative path already under OUT, also try extract into backend
tar -tzf "$SRC/media-biz.tgz" 2>/dev/null | head -3 || true

docker compose exec -T backend python manage.py shell -c "
from accounts.models import Customer
from sales.models import Party, Sale
from stock.models import Product
from service.models import Job, Device
from crew.models import CrewMember
print('users', Customer.objects.count(), '(unchanged expected)')
print('parties', Party.objects.count(), 'sales', Sale.objects.count(), 'products', Product.objects.count())
print('jobs', Job.objects.count(), 'devices', Device.objects.count(), 'crew', CrewMember.objects.count())
"

echo "==> Done. Portal http://127.0.0.1:8000 — login with your local users."
