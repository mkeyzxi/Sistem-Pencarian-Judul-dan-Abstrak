#!/usr/bin/env bash
# ============================================================================
# Jalankan backend dengan multi-worker untuk kapasitas tinggi
#
# Cara pakai:
#   bash run.sh                    → 4 worker (default)
#   WORKERS=8 bash run.sh          → 8 worker
#
# Worker lebih banyak = bisa layani lebih banyak user concurrent,
# tapi ChromaDB di-load per worker (resource trade-off).
# ============================================================================

set -e

# ── Ambil WORKERS dari environment atau default 4 ──
WORKERS=${WORKERS:-4}
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}

echo "═══════════════════════════════════════════════════════════════"
echo "  🚀 Sistem Pencarian Skripsi — Starting Server"
echo "  Workers : ${WORKERS}"
echo "  Host    : ${HOST}"
echo "  Port    : ${PORT}"
echo "  Docs    : http://${HOST}:${PORT}/docs"
echo "  Health  : http://${HOST}:${PORT}/api/health"
echo "═══════════════════════════════════════════════════════════════"

cd "$(dirname "$0")"

# ── Jalankan dengan uvicorn multi-worker ──
# reload=False: wajib untuk multi-worker (reload hanya untuk 1 process)
uvicorn app.main:app \
    --host "${HOST}" \
    --port "${PORT}" \
    --workers "${WORKERS}" \
    --log-level info \
    --timeout-keep-alive 60
