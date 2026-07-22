#!/usr/bin/env bash
#
# deploy_model.sh — deploy modelu detektora Mac → VPS (wariant B: symlink).
#
# Użycie:
#   ./tools/deploy_model.sh <lokalny_model.pt> <wersja> [próg]
#
# Przykłady:
#   ./tools/deploy_model.sh runs/detect/bird_v2/weights/best.pt v2 0.5
#   ./tools/deploy_model.sh runs/detect/bird_v2/weights/best.pt v2      # próg bez zmian
#
set -euo pipefail

# --- konfiguracja VPS ---
VPS="root@100.75.59.30"
MODELS_DIR="/opt/bird-api/models"
ENV_FILE="/opt/bird-api/.env"
SERVICE="bird-yolo"
HEALTH_URL="http://127.0.0.1:8002/health"
DEFAULT_CONF="0.45"
HEALTH_TIMEOUT=30

# --- argumenty ---
if [[ $# -lt 2 ]]; then
  echo "Użycie: $0 <lokalny_model.pt> <wersja> [próg]" >&2
  echo "Przykład: $0 runs/detect/bird_v2/weights/best.pt v2 0.5" >&2
  exit 1
fi

LOCAL_MODEL="$1"
VERSION="$2"
CONF="${3:-}"

if [[ ! -f "$LOCAL_MODEL" ]]; then
  echo "BŁĄD: plik modelu nie istnieje: $LOCAL_MODEL" >&2
  exit 1
fi

REMOTE_MODEL="bird_${VERSION}.pt"
REMOTE_PATH="${MODELS_DIR}/${REMOTE_MODEL}"

echo "==> Deploy modelu"
echo "    lokalny:  $LOCAL_MODEL"
echo "    zdalny:   $REMOTE_PATH"
echo "    wersja:   $VERSION"
if [[ -n "$CONF" ]]; then
  echo "    próg:     $CONF (zmiana w .env)"
else
  echo "    próg:     bez zmian"
fi
echo

echo "==> [1/5] Kopiowanie modelu na VPS..."
scp "$LOCAL_MODEL" "${VPS}:${REMOTE_PATH}"

echo "==> [2/5] Przepięcie symlinku + restart + health-check (zdalnie)..."
ssh "$VPS" CONF="$CONF" REMOTE_MODEL="$REMOTE_MODEL" \
    MODELS_DIR="$MODELS_DIR" ENV_FILE="$ENV_FILE" SERVICE="$SERVICE" \
    HEALTH_URL="$HEALTH_URL" HEALTH_TIMEOUT="$HEALTH_TIMEOUT" 'bash -s' <<'REMOTE'
set -euo pipefail
cd "$MODELS_DIR"

if [[ -L bird_active.pt ]]; then
  PREV_TARGET="$(readlink bird_active.pt)"
else
  PREV_TARGET=""
fi
echo "    poprzedni model: ${PREV_TARGET:-(brak symlinku)}"

ENV_BAK=""
if [[ -n "$CONF" ]]; then
  ENV_BAK="${ENV_FILE}.bak-$(date +%Y%m%d-%H%M%S)"
  cp "$ENV_FILE" "$ENV_BAK"
  sed -i "s|^YOLO_MIN_CONFIDENCE=.*|YOLO_MIN_CONFIDENCE=${CONF}|" "$ENV_FILE"
  echo "    .env: YOLO_MIN_CONFIDENCE=${CONF} (backup: $ENV_BAK)"
fi

ln -sfn "$REMOTE_MODEL" bird_active.pt
echo "    symlink: bird_active.pt -> $(readlink bird_active.pt)"

systemctl restart "$SERVICE"

echo "    czekam na /health (do ${HEALTH_TIMEOUT}s)..."
OK=0
for i in $(seq 1 "$HEALTH_TIMEOUT"); do
  RESP="$(curl -s "$HEALTH_URL" 2>/dev/null || true)"
  if echo "$RESP" | grep -q '"loaded":true'; then
    OK=1
    echo "    OK po ${i}s: $RESP"
    break
  fi
  sleep 1
done

if [[ "$OK" -ne 1 ]]; then
  echo "    !!! health-check nieudany — ROLLBACK" >&2
  if [[ -n "$PREV_TARGET" ]]; then
    ln -sfn "$PREV_TARGET" bird_active.pt
    echo "    symlink cofnięty na: $PREV_TARGET" >&2
  fi
  if [[ -n "$ENV_BAK" ]]; then
    cp "$ENV_BAK" "$ENV_FILE"
    echo "    .env przywrócony z backupu" >&2
  fi
  systemctl restart "$SERVICE"
  echo "    usługa zrestartowana po rollbacku" >&2
  exit 2
fi
REMOTE

echo
echo "==> Deploy zakończony sukcesem. Aktywny model: bird_${VERSION}.pt"
