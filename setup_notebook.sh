#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
python -m ipykernel install --user --name tna5373 --display-name "Python (TNA5373)"

if command -v git-lfs >/dev/null 2>&1; then
  git lfs install
  git lfs pull
fi

echo
echo "Ambiente configurado."
echo "Para abrir o notebook, execute:"
echo "  ./abrir_notebook.sh"
