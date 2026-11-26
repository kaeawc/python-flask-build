"""WSGI entry point for production servers: `gunicorn python_flask_build.wsgi:app`."""

from python_flask_build.app import create_app

app = create_app()
