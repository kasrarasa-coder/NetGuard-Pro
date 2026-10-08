from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
import mimetypes

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
FILES = {
    "/download/windows": ROOT / "downloads" / "NetGuardPro_Windows.zip",
    "/download/linux": ROOT / "downloads" / "NetGuardPro_Linux.tar.gz",
    "/download/mobile": ROOT / "downloads" / "NetGuardPro_Mobile_PWA.zip",
    "/download/full": ROOT / "downloads" / "NetGuardPro_FULL.zip",
    "/download/app": ROOT / "netguard_pro.py",
}

class Handler(BaseHTTPRequestHandler):
    def send_bytes(self, data, content_type, filename=None):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        if filename:
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlparse(self.path).path

        if path in FILES:
            p = FILES[path]
            if not p.exists():
                self.send_error(404, "File not found")
                return
            data = p.read_bytes()
            ctype = mimetypes.guess_type(str(p))[0] or "application/octet-stream"
            self.send_bytes(data, ctype, p.name)
            return

        if path == "/":
            path = "/index.html"

        target = (WEB / path.lstrip("/")).resolve()
        if not str(target).startswith(str(WEB.resolve())) or not target.is_file():
            self.send_error(404, "Not found")
            return

        data = target.read_bytes()
        ctype = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        self.send_bytes(data, ctype)

    def log_message(self, fmt, *args):
        print(f"[NetGuard Web] {self.address_string()} - {fmt % args}")

if __name__ == "__main__":
    host, port = "127.0.0.1", 8765
    print(f"NetGuard Pro website: http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    ThreadingHTTPServer((host, port), Handler).serve_forever()
