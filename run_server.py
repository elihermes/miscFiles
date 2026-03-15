# Simple Python HTTP server launcher for webfiles directory
# Usage: python3 run_server.py

import http.server
import json
import os
import socketserver
import threading
from urllib.parse import urlparse
import webbrowser
from pathlib import Path

PORT = 8000
SCRIPT_DIR = Path(__file__).resolve().parent
DIRECTORY = SCRIPT_DIR

os.chdir(DIRECTORY)


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def build_local_tree(root: Path):
    tree = []
    for dirpath, dirnames, filenames in os.walk(root):
        current_dir = Path(dirpath)
        rel_dir = current_dir.relative_to(root).as_posix()
        if rel_dir == ".":
            rel_dir = ""

        # Keep the browser list clean from internal folders.
        dirnames[:] = [d for d in dirnames if d not in {".git", "__pycache__"}]

        for dirname in dirnames:
            rel_path = f"{rel_dir}/{dirname}" if rel_dir else dirname
            tree.append({"path": rel_path, "type": "tree"})

        for filename in filenames:
            rel_path = f"{rel_dir}/{filename}" if rel_dir else filename
            tree.append({"path": rel_path, "type": "blob"})

    return tree


class LocalAwareHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/local-tree":
            payload = {"tree": build_local_tree(DIRECTORY)}
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        super().do_GET()


Handler = LocalAwareHandler

with ReusableTCPServer(("", PORT), Handler) as httpd:
    url = f"http://localhost:{PORT}"
    print(f"Serving at {url} (directory: {DIRECTORY})")

    # Open browser shortly after server starts without blocking startup.
    threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    httpd.serve_forever()
