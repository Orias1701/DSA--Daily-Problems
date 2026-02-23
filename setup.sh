#!/usr/bin/env bash
# Setup môi trường ảo trên macOS / Linux.
# Chạy: ./setup.sh   hoặc   bash setup.sh

set -e
cd "$(dirname "$0")"

if ! command -v python3 &>/dev/null; then
  if command -v python &>/dev/null; then
    PY=python
  else
    echo "Cần cài Python 3 (python3 hoặc python)."
    exit 1
  fi
else
  PY=python3
fi

echo "Đang setup môi trường ảo..."
$PY setup_venv.py

echo ""
echo "Kích hoạt venv rồi chạy bot:"
echo "  source .venv/bin/activate"
echo "  python main.py"
