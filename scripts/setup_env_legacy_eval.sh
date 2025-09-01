#!/usr/bin/env bash
set -euo pipefail

# Create a Python 3.9 environment for legacy evaluation (scispaCy + en_core_sci_sm)

VENV_DIR=${VENV_DIR:-.venv-legacy}

# Try to find a working python3.9 binary
if command -v python3.9 &>/dev/null; then
    PYTHON_BIN=python3.9
elif command -v pyenv &>/dev/null && pyenv versions --bare | grep -q '^3\.9'; then
    PYTHON_BIN=$(pyenv which python3.9)
else
    echo "Error: Python 3.9 not found."
    echo "Please install Python 3.9 via:"
    echo "  - Ubuntu/Debian: sudo add-apt-repository ppa:deadsnakes/ppa && sudo apt install python3.9 python3.9-venv"
    echo "  - Or with pyenv: pyenv install 3.9.18"
    exit 1
fi

echo "Using ${PYTHON_BIN} to create legacy eval venv: ${VENV_DIR}"
"${PYTHON_BIN}" -m venv "${VENV_DIR}"

source "${VENV_DIR}/bin/activate"

python -m pip install --upgrade pip wheel setuptools
pip install -r requirements-eval-legacy.txt

# Optional: install scispaCy model automatically if provided
# - Set SCISPACY_MODEL to a local path (tar.gz wheel) or URL
if [[ -n "${SCISPACY_MODEL:-}" ]]; then
    echo "Installing scispaCy model from ${SCISPACY_MODEL}"
    pip install "${SCISPACY_MODEL}" || echo "Warning: failed to install model automatically; install manually."
fi

echo
echo "Done. Activate with: source ${VENV_DIR}/bin/activate"
echo "Note: Install a compatible scispaCy model if not already installed, for example:"
echo " pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.4/en_core_sci_sm-0.5.4.tar.gz"
echo " pip install nmslib --only-binary=:all:" 
