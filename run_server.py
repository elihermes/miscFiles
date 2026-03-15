# Simple Python HTTP server launcher for webfiles directory
# Usage: python3 run_server.py

import http.server
import os
import socketserver
import threading
import webbrowser
from pathlib import Path

PORT = 8000
SCRIPT_DIR = Path(__file__).resolve().parent
DIRECTORY = SCRIPT_DIR

os.chdir(DIRECTORY)


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


Handler = http.server.SimpleHTTPRequestHandler

with ReusableTCPServer(("", PORT), Handler) as httpd:
    url = f"http://localhost:{PORT}"
    print(f"Serving at {url} (directory: {DIRECTORY})")

    # Open browser shortly after server starts without blocking startup.
    threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    httpd.serve_forever()
