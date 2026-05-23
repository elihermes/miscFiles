#!/bin/bash
cd "$(dirname "$0")"

if curl -fsS --max-time 2 http://127.0.0.1:8000/ >/dev/null; then
	open "http://localhost:8000/"
	exit 0
fi

python3 run_server.py
