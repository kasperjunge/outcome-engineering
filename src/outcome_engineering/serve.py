from __future__ import annotations

import json
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from outcome_engineering.graph import (
    create_node,
    delete_node,
    write_marker,
)
from outcome_engineering.read import build_graph_payload, issue_dicts
from outcome_engineering.ui import graph_page


def _issues(root: Path) -> list[dict]:
    return issue_dicts(root)


class GraphRequestHandler(BaseHTTPRequestHandler):
    """Serves the editable graph UI and a small JSON CRUD API over one graph.

    The bound graph root is injected as ``root`` by :func:`make_server`. Structural
    mutations (create/delete) are enforced and rejected with 400 on rule
    violations; marker edits always land and report any resulting validation
    issues so the UI can surface them without discarding the edit.
    """

    root: Path
    server_version = "oe-serve"

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002,D401 - quiet by default
        return

    # -- helpers --------------------------------------------------------------
    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html: str) -> None:
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", 0) or 0)
        if not length:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return {}

    def _selector(self, prefix: str) -> str:
        return unquote(urlparse(self.path).path[len(prefix) :])

    # -- routes ---------------------------------------------------------------
    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            self._send_html(graph_page())
        elif path == "/favicon.ico":
            self.send_response(204)
            self.send_header("Content-Length", "0")
            self.end_headers()
        elif path == "/api/graph":
            self._send_json(200, build_graph_payload(self.root))
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/nodes":
            self._send_json(404, {"error": "not found"})
            return
        data = self._read_json()
        try:
            node = create_node(
                self.root,
                kind=data["kind"],
                slug=data["slug"],
                title=data.get("title"),
                under=data.get("under"),
            )
        except KeyError as error:
            self._send_json(400, {"error": f"missing field: {error.args[0]}"})
            return
        except (ValueError, FileExistsError) as error:
            self._send_json(400, {"error": str(error)})
            return
        self._send_json(201, {"id": node.id, "issues": _issues(self.root)})

    def do_PUT(self) -> None:
        prefix = "/api/nodes/"
        if not urlparse(self.path).path.startswith(prefix):
            self._send_json(404, {"error": "not found"})
            return
        data = self._read_json()
        if "content" not in data:
            self._send_json(400, {"error": "missing field: content"})
            return
        try:
            node = write_marker(self.root, self._selector(prefix), data["content"])
        except ValueError as error:
            self._send_json(400, {"error": str(error)})
            return
        self._send_json(200, {"id": node.id, "issues": _issues(self.root)})

    def do_DELETE(self) -> None:
        prefix = "/api/nodes/"
        if not urlparse(self.path).path.startswith(prefix):
            self._send_json(404, {"error": "not found"})
            return
        params = parse_qs(urlparse(self.path).query)
        cascade = params.get("cascade", ["false"])[0] == "true"
        try:
            delete_node(self.root, self._selector(prefix), cascade=cascade)
        except ValueError as error:
            self._send_json(400, {"error": str(error)})
            return
        self._send_json(200, {"ok": True, "issues": _issues(self.root)})


def make_server(root: Path, host: str = "127.0.0.1", port: int = 8000) -> ThreadingHTTPServer:
    """Build (but do not start) a server bound to one graph root.

    Binds loopback only by default; the graph is the local checkout and git is the
    collaboration layer, so there is nothing to expose to the network.
    """
    handler = type("BoundGraphRequestHandler", (GraphRequestHandler,), {"root": root.resolve()})
    return ThreadingHTTPServer((host, port), handler)


def serve(root: Path, host: str = "127.0.0.1", port: int = 8000, open_browser: bool = True) -> None:
    httpd = make_server(root, host=host, port=port)
    bound_host, bound_port = httpd.server_address[0], httpd.server_address[1]
    url = f"http://{bound_host}:{bound_port}/"
    print(f"Serving {root} at {url} (Ctrl-C to stop)")
    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        httpd.server_close()
