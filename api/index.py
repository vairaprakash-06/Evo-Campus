import os
import sys
import urllib.parse

# Ensure root directory is on the python search path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app

class VercelPathFixMiddleware:
    """
    WSGI middleware that fixes PATH_INFO when Vercel rewrites requests to /api/index.
    Restores the original user-requested path from __path__ query param.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        qs = environ.get("QUERY_STRING", "")
        if "__path__=" in qs:
            params = urllib.parse.parse_qs(qs)
            injected_path = params.get("__path__", [""])[0]
            if injected_path:
                clean_path = "/" + injected_path.lstrip("/")
                environ["PATH_INFO"] = clean_path
                filtered = [p for p in qs.split("&") if not p.startswith("__path__=")]
                environ["QUERY_STRING"] = "&".join(filtered)
        elif environ.get("PATH_INFO") in ("/api/index", "/api/index.py"):
            environ["PATH_INFO"] = "/"
        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathFixMiddleware(app.wsgi_app)
