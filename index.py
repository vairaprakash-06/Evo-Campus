"""
Root entry point alias for Vercel and WSGI servers.
"""
from app import app

if __name__ == "__main__":
    app.run()
