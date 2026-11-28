[![Commit](https://github.com/kaeawc/python-flask-build/actions/workflows/commit.yml/badge.svg)](https://github.com/kaeawc/python-flask-build/actions/workflows/commit.yml)

# Python Flask Build

Python build tooling, references and a CI pipeline for a Flask web server. The goal is to show
current best practice and to be a good foundation for a new Flask project. Sibling of
[golang-build](https://github.com/kaeawc/golang-build) and
[rust-build](https://github.com/kaeawc/rust-build).

- **uv** for Python, dependencies and the lockfile; nothing else to install.
- **ruff** (lint + format), **mypy --strict**, **pytest** with a branch-coverage gate.
- **bandit** and **pip-audit** for security; **actionlint** for workflows; CodeQL via GitHub.
- **gunicorn** in production, in a **distroless, non-root** image with digest-pinned bases.
- App factory, validated configuration, request IDs, JSON logs, JSON errors, health probes.

## Getting started

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # or: brew install uv
make sync      # creates .venv with the app and dev tools from uv.lock
make run       # dev server on http://127.0.0.1:5000
curl localhost:5000/status
```

`make help` lists every target. Before pushing, run `make check`; `make ci` runs everything CI does
except building the image.

| Target | What it does |
| --- | --- |
| `make check` | lock-check, format check, ruff, mypy, tests with coverage gate |
| `make ci` | `check` plus bandit, pip-audit, actionlint and tests on Python 3.11–3.14 |
| `make fmt` / `make lint-fix` | apply formatting / ruff's automatic fixes |
| `make serve` | gunicorn, as in production |
| `make docker` / `make docker-run` | build / build and run `ci/Dockerfile` |

## Endpoints

| Route | Purpose |
| --- | --- |
| `GET /status` | `{"status": "OK", "message": ..., "version": ...}` |
| `GET /healthz` | Liveness: the process is serving. Never checks dependencies. |
| `GET /readyz` | Readiness: runs each check passed to `create_app(readiness_checks=...)`; 503 if any fails. |

Every response carries an `X-Request-ID` (an inbound one is kept if it is a short plain token) and
security headers. Errors are JSON: `{"error": {"code": "not_found", "message": ..., "requestId": ...}}`.

## Configuration

Read from the environment once at startup and validated; an invalid value stops the app with an
error naming the variable.

| Variable | Default | Notes |
| --- | --- | --- |
| `PORT` | `5000` | 1–65535. Used by both the dev server and gunicorn. |
| `HOST` | `127.0.0.1` | Dev server only; gunicorn binds `0.0.0.0` in the container. |
| `DEBUG` | `false` | Dev server debug mode (`true`/`false`, `1`/`0`, `yes`/`no`, `on`/`off`). |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. |
| `LOG_FORMAT` | `text` | `text` or `json` (one object per line). |
| `WEB_CONCURRENCY` | `2` | gunicorn worker processes. |
| `GUNICORN_THREADS` | `4` | Threads per gunicorn worker. |

## Layout

```
src/python_flask_build/   the app: create_app, config, health, middleware, errors, logs, wsgi
tests/                    pytest, one file per module
gunicorn.conf.py          production server settings
ci/Dockerfile             uv build stage -> distroless Python, non-root
.github/workflows/        commit.yml: CI; every job is a make target
.buildkite/               Buildkite trial: the same make targets on hosted agents
```

## Docker

```bash
make docker-run           # http://localhost:5000
```

The image installs the locked dependencies with uv in a Debian 13 build stage and copies only the
virtualenv onto `gcr.io/distroless/python3-debian13:nonroot`: no shell, no package manager, uid
65532. CI runs it with a read-only root filesystem and pushes `ghcr.io/kaeawc/python-build` from
`main`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Coding agents: [AGENTS.md](AGENTS.md). Security reports:
[SECURITY.md](SECURITY.md).
