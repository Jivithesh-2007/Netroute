#!/usr/bin/env bash
# ==============================================================================
# start.sh — Quick Launch Script for NetRoute Streamlit Web Application
# ==============================================================================

set -e

# Resolve the absolute path to the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================================"
echo "  🚀 NetRoute — Network Packet Routing Simulator"
echo "========================================================"

# Check and activate virtual environment
if [ -d "$SCRIPT_DIR/.venv" ]; then
    echo "✓ Activating virtual environment (.venv)..."
    # shellcheck source=/dev/null
    source "$SCRIPT_DIR/.venv/bin/activate"
elif [ -d "$SCRIPT_DIR/venv" ]; then
    echo "✓ Activating virtual environment (venv)..."
    # shellcheck source=/dev/null
    source "$SCRIPT_DIR/venv/bin/activate"
else
    echo "⚠️  No .venv directory found in $SCRIPT_DIR."
    echo "   Attempting to use system Python / Streamlit..."
fi

# Verify streamlit is available
if ! command -v streamlit &> /dev/null; then
    echo "❌ Error: 'streamlit' is not installed or not in PATH."
    echo "   Please run: pip install -r requirements.txt"
    exit 1
fi

echo "✓ Streamlit detected: $(streamlit --version)"
echo "✓ Launching application on http://localhost:8501 ..."
echo "--------------------------------------------------------"
echo "  Press Ctrl + C in this terminal to stop the server."
echo "========================================================"
echo ""

# Launch Streamlit and forward any optional arguments passed to start.sh
exec streamlit run "$SCRIPT_DIR/main.py" "$@"
