#!/usr/bin/env bash
# Chwezi PDF Suite - Linux / macOS installer / updater
# Run once on a new machine to install everything, or again to update.

set -euo pipefail

PYTHON_MIN_MAJOR=3
PYTHON_MIN_MINOR=10

# Helpers
step()  { echo ""; echo "==> $*"; }
ok()    { echo "    OK  $*"; }
warn()  { echo "    --  $*"; }
fail()  { echo "    ERR $*" >&2; exit 1; }

# Banner
echo ""
echo "====================================================="
echo "  Chwezi PDF Suite - Install / Update (Unix)     "
echo "====================================================="

# 1. Detect OS
step "Detecting operating system"
OS="unknown"
if [[ "$(uname)" == "Darwin" ]]; then
    OS="macos"
    ok "macOS detected"
elif [[ -f /etc/os-release ]]; then
    . /etc/os-release
    case "$ID" in
        ubuntu|debian|linuxmint|pop) OS="debian" ;;
        fedora|rhel|centos|rocky)    OS="fedora"  ;;
        arch|manjaro)                OS="arch"    ;;
        *)                           OS="linux"   ;;
    esac
    ok "Linux detected: $PRETTY_NAME"
else
    warn "Unknown OS -- will attempt generic install"
    OS="linux"
fi

# 2. Python
step "Checking Python installation"

PYTHON_CMD=""
for candidate in python3 python python3.12 python3.11 python3.10; do
    if command -v "$candidate" &>/dev/null; then
        ver=$("$candidate" --version 2>&1)
        major=$(echo "$ver" | grep -oP '(?<=Python )\d+' || true)
        minor=$(echo "$ver" | grep -oP '(?<=Python \d\.)\d+' || true)
        if [[ "${major:-0}" -ge $PYTHON_MIN_MAJOR && "${minor:-0}" -ge $PYTHON_MIN_MINOR ]]; then
            PYTHON_CMD="$candidate"
            ok "Found: $ver"
            break
        fi
    fi
done

if [[ -z "$PYTHON_CMD" ]]; then
    echo "    Python $PYTHON_MIN_MAJOR.$PYTHON_MIN_MINOR+ not found. Installing..."

    case "$OS" in
        debian)
            sudo apt-get update -qq
            sudo apt-get install -y python3 python3-pip python3-venv
            PYTHON_CMD="python3"
            ;;
        fedora)
            sudo dnf install -y python3 python3-pip
            PYTHON_CMD="python3"
            ;;
        arch)
            sudo pacman -Sy --noconfirm python python-pip
            PYTHON_CMD="python3"
            ;;
        macos)
            if ! command -v brew &>/dev/null; then
                fail "Homebrew not found. Install it from https://brew.sh/ then re-run this script."
            fi
            brew install python
            PYTHON_CMD="python3"
            ;;
        *)
            fail "Cannot auto-install Python on this OS. Install Python $PYTHON_MIN_MAJOR.$PYTHON_MIN_MINOR+ manually then re-run."
            ;;
    esac
    ok "Python installed: $($PYTHON_CMD --version)"
fi

# 3. pip
step "Upgrading pip"

if ! "$PYTHON_CMD" -m pip --version &>/dev/null 2>&1; then
    case "$OS" in
        debian) sudo apt-get install -y python3-pip ;;
        fedora) sudo dnf install -y python3-pip ;;
        arch)   sudo pacman -Sy --noconfirm python-pip ;;
        macos)  brew install python ;;
    esac
fi

"$PYTHON_CMD" -m pip install --upgrade pip --quiet
ok "pip up to date"

# 4. Dependencies
step "Installing / upgrading project dependencies"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REQ="$SCRIPT_DIR/requirements.txt"

[[ -f "$REQ" ]] || fail "requirements.txt not found at $REQ"

"$PYTHON_CMD" -m pip install --upgrade -r "$REQ"
ok "All dependencies installed / up to date"

# Done
echo ""
echo "====================================================="
echo "  Setup complete! Run the suite with:"
echo "    $PYTHON_CMD index-app.py"
echo "====================================================="
echo ""
