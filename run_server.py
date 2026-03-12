# Simple Python HTTP server launcher for webfiles directory
# Usage: python3 run_server.py

import http.server
import socketserver
import os

PORT = 8000
DIRECTORY = "webfiles"

os.chdir(DIRECTORY)

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at http://localhost:{PORT} (directory: {DIRECTORY})")
    httpd.serve_forever()
