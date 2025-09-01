#!/usr/bin/env bash
set -euo pipefail

# Create a Python 3.12 environment for BRATsynthetic + evaluation (spaCy 3.8 + en_core_web_lg)

VENV_DIR=${VENV_DIR:-.venv-main}
PYTHON_BIN=${PYTHON_BIN:-python3.12}

echo "Creating main venv (${VENV_DIR}) with ${PYTHON_BIN}"
${PYTHON_BIN} -m venv "${VENV_DIR}"

ACTIVATE_SCRIPT="${VENV_DIR}/bin/activate"
source "${ACTIVATE_SCRIPT}"

python -m pip install --upgrade pip wheel setuptools
pip install -r requirements-main.txt

echo "Downloading spaCy model en_core_web_lg..."
python -m spacy download en_core_web_lg

echo "Done. Activate with: source ${VENV_DIR}/bin/activate"
