#!/usr/bin/env bash
# birds.garden — backup DB + zdjęcia (gotowiec pod zadanie A).
#
# Teraz: pominięte świadomie (do produkcji daleko). Gdy zechcesz A:
#   chmod +x tools/backup_db.sh
#   crontab -e   →   15 3 * * *  /opt/bird-api/tools/backup_db.sh
# I tyle — A zrobione. Czyta /opt/bird-api/.env, więc działa po rotacji sekretów.

set -euo pipefail

ENV_FILE="${ENV_FILE:-/opt/bird-api/.env}"
[ -f "$ENV_FILE" ] && set -a && . "$ENV_FILE" && set +a

BACKUP_DIR="${BACKUP_DIR:-/opt/bird-api/backups}"
PHOTOS_DIR="${PHOTOS_DIR:-/opt/bird-api/photos}"
KEEP_DAYS="${BACKUP_KEEP_DAYS:-14}"
STAMP="$(date +%Y-%m-%d_%H%M)"

mkdir -p "$BACKUP_DIR"

# ── Dump bazy (jedyny prawdziwy asset danych: historia detekcji) ───────────
PGPASSWORD="$DB_PASSWORD" pg_dump \
    -h "${DB_HOST:-localhost}" -p "${DB_PORT:-5432}" \
    -U "${DB_USER:-bird}" -d "${DB_NAME:-birddb}" \
    | gzip > "$BACKUP_DIR/birddb_${STAMP}.sql.gz"

# ── Zdjęcia z detekcji (przyrostowo, twarde linki gdy nic się nie zmieniło) ─
if [ -d "$PHOTOS_DIR" ]; then
    tar czf "$BACKUP_DIR/photos_${STAMP}.tar.gz" -C "$(dirname "$PHOTOS_DIR")" "$(basename "$PHOTOS_DIR")"
fi

# ── Rotacja: trzymaj ostatnie N dni ────────────────────────────────────────
find "$BACKUP_DIR" -name 'birddb_*.sql.gz' -mtime +"$KEEP_DAYS" -delete
find "$BACKUP_DIR" -name 'photos_*.tar.gz' -mtime +"$KEEP_DAYS" -delete

echo "backup ok: $BACKUP_DIR  (birddb_${STAMP}.sql.gz)"
# Tygodniowy snapshot Hetzner robisz osobno w panelu (drugi poziom ochrony).
