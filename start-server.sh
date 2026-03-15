#!/usr/bin/env bash
# Script to run Python server from הדגמות מרכז שרווץ רייסמן מכון ויצמן

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/webfiles/הדגמות מרכז שרווץ רייסמן מכון ויצמן"

if command -v python3 >/dev/null 2>&1; then
	PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
	PYTHON_CMD="python"
elif command -v py >/dev/null 2>&1; then
	PYTHON_CMD="py -3"
else
	echo "Python was not found in PATH."
	exit 1
fi

eval "$PYTHON_CMD ../../run_server.py"
