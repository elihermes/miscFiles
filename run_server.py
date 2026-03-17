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
QUESTION_TOPICS_PATH = DIRECTORY / "webfiles" / "פתרונות שאלות בגרות" / "מכניקה שאלות בגרות" / "question-topics.json"

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

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/save-question-topics":
            self.send_error(404, "Unknown API endpoint")
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_error(400, "Invalid Content-Length")
            return

        try:
            raw_body = self.rfile.read(content_length)
            payload = json.loads(raw_body.decode("utf-8"))
            normalized = self._normalize_question_topics_payload(payload)
            QUESTION_TOPICS_PATH.write_text(
                json.dumps(normalized, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8"
            )
        except ValueError as exc:
            body = json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False).encode("utf-8")
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        body = json.dumps({"ok": True}, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _normalize_question_topics_payload(self, payload):
        if not isinstance(payload, dict):
            raise ValueError("Payload must be an object")

        topics = payload.get("topics")
        questions = payload.get("questions")
        if not isinstance(topics, list) or not all(isinstance(topic, str) for topic in topics):
            raise ValueError("Field 'topics' must be an array of strings")
        if not isinstance(questions, list):
            raise ValueError("Field 'questions' must be an array")

        normalized_questions = []
        allowed_topics = set(topics)
        for question in questions:
            if not isinstance(question, dict):
                raise ValueError("Each question must be an object")

            question_id = question.get("id")
            title = question.get("title")
            path = question.get("path")
            question_topics = question.get("topics")

            if not isinstance(question_id, str) or not question_id.strip():
                raise ValueError("Each question must include a non-empty string 'id'")
            if not isinstance(title, str) or not title.strip():
                raise ValueError("Each question must include a non-empty string 'title'")
            if not isinstance(path, str) or not path.strip():
                raise ValueError("Each question must include a non-empty string 'path'")
            if not isinstance(question_topics, list) or not all(isinstance(topic, str) for topic in question_topics):
                raise ValueError("Each question must include 'topics' as an array of strings")

            filtered_topics = []
            for topic in question_topics:
                if topic in allowed_topics and topic not in filtered_topics:
                    filtered_topics.append(topic)

            normalized_questions.append({
                "id": question_id,
                "title": title,
                "path": path,
                "topics": filtered_topics,
            })

        return {
            "topics": topics,
            "questions": normalized_questions,
        }


Handler = LocalAwareHandler

with ReusableTCPServer(("", PORT), Handler) as httpd:
    url = f"http://localhost:{PORT}"
    print(f"Serving at {url} (directory: {DIRECTORY})")

    # Open browser shortly after server starts without blocking startup.
    threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    httpd.serve_forever()
