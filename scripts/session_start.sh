#!/usr/bin/env bash
# SessionStart hook: prepare the environment for a Claude Code (web) session.
# Best-effort and non-fatal -- a fresh container may be offline for pip; the
# dependency-free smoke test still validates the stage interfaces either way.
set -uo pipefail

cd "$(dirname "$0")/.." || exit 0

echo "[session_start] installing pinned dependencies (best-effort)..."
python3 -m pip install --quiet --disable-pip-version-check -r requirements.txt 2>/dev/null \
  && echo "[session_start] dependencies installed" \
  || echo "[session_start] pip unavailable/offline -- skipping (smoke test is dependency-free)"

echo "[session_start] running smoke tests..."
python3 smoke_tests.py || echo "[session_start] smoke tests reported a failure -- see output above"

exit 0
