# Gunicorn settings, loaded automatically from the working directory.
# PORT and LOG_LEVEL come from Config; WEB_CONCURRENCY sets workers, GUNICORN_THREADS threads per
# worker, and GUNICORN_CMD_ARGS can override anything here.
import os

from python_flask_build.config import Config

_config = Config.from_env()

wsgi_app = "python_flask_build.wsgi:app"
# Containers publish the port, so bind every interface; HOST only applies to the dev server.
bind = f"0.0.0.0:{_config.port}"
workers = int(os.environ.get("WEB_CONCURRENCY", "2"))
threads = int(os.environ.get("GUNICORN_THREADS", "4"))
# On SIGTERM, workers get this long to finish in-flight requests.
graceful_timeout = 20
timeout = 30
keepalive = 5
accesslog = None  # the app writes its own access log, with request IDs
errorlog = "-"
loglevel = _config.log_level.lower()
# The control socket (gunicornc) would write under $HOME; containers are managed by signals instead.
control_socket_disable = True
# Worker heartbeats on tmpfs, so a slow or read-only disk cannot stall them. Gunicorn creates the
# file with mkstemp (random name, mode 0600), so a shared directory is safe here.
_SHM = "/dev/shm"  # noqa: S108  # nosec B108
worker_tmp_dir = _SHM if os.path.isdir(_SHM) else None
