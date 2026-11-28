# python-flask-build

Flask web server template with a uv-based build and a CI pipeline. Sibling of
[golang-build](https://github.com/kaeawc/golang-build) and
[rust-build](https://github.com/kaeawc/rust-build).

## Working rules

- Python only, managed with uv. `pyproject.toml` is the only place dependencies are declared and
  `uv.lock` is committed; never add `requirements*.txt`, `setup.py`, or `pip install` steps.
  Runtime dependencies go in `[project] dependencies`, tools in the `dev` dependency group. Add one
  with `uv add <pkg>` (or `uv add --dev <pkg>`) so the lock updates with it. Only add a runtime
  dependency for clear value.
- Build the app with `create_app()` (`src/python_flask_build/app.py`). Never create a module-level
  `Flask(...)` elsewhere; `wsgi.py` is the only module that instantiates it at import time.
- Routes live in blueprints registered by `create_app`. Errors leave through the JSON envelope in
  `errors.py` (`{"error": {"code", "message", "requestId"}}`); never return HTML error pages or
  exception text to clients.
- Configuration is read once, in `Config.from_env` (`config.py`), which validates every variable
  and raises `ConfigError` naming it. Don't call `os.environ`/`os.getenv` from request code; add a
  field to `Config` instead and document it in the README's configuration table.
- Log with `logging.getLogger(__name__)` and pass structured fields through `extra=`; never
  `print`. Logs go to stdout only (no log files: containers collect stdout).
- Time and IDs are injectable for tests (`create_app(new_request_id=...)`,
  `middleware.install(clock=...)`); tests use fakes, never sleeps.
- Production runs gunicorn with `gunicorn.conf.py`; the Flask dev server
  (`python -m python_flask_build`) is for local work only.
- Keep `/status`, `/healthz` and `/readyz` working: the image smoke test in CI calls all three.
  Add dependency checks to readiness through `create_app(readiness_checks=...)`, never to
  `/healthz`.

## Build & validate

```bash
make help          # every target
make sync          # install app + dev tools into .venv from uv.lock
make check         # pre-push gate: lock-check, fmt-check, lint, typecheck, test (coverage gate)
make ci            # everything CI runs except the image build: adds bandit, pip-audit, actionlint,
                   # and the tests on every supported Python
make fmt           # ruff format + import sort
make run           # dev server on 127.0.0.1:5000
make serve         # gunicorn, as in production
make docker        # build ci/Dockerfile
```

While iterating: `uv run pytest tests/test_health.py -k readyz`. After any change, run
`make check` before pushing.

## Git

- Branch from `main` and open a pull request; nobody pushes to `main` directly. Agent branches use
  the `work/` prefix.
- PR titles are imperative commit subjects (they become the squash-merge subject).

## Project map

- `src/python_flask_build/app.py`: `create_app(config, readiness_checks=, new_request_id=)`.
- `src/python_flask_build/config.py`: `Config` (frozen dataclass), `Config.from_env`, `ConfigError`.
- `src/python_flask_build/health.py`: `/status` (legacy contract), `/healthz` (liveness),
  `/readyz` (runs readiness checks, 503 when one raises).
- `src/python_flask_build/middleware.py`: request IDs (`X-Request-ID`, inbound value kept only if it
  matches `[A-Za-z0-9._-]{1,64}`), access log, security headers.
- `src/python_flask_build/errors.py`: JSON error envelope for HTTP errors and unhandled exceptions.
- `src/python_flask_build/logs.py`: stdout logging, `text` or `json` (`LOG_FORMAT`).
- `src/python_flask_build/wsgi.py`: `app` for gunicorn. `__main__.py`: the dev server.
- `gunicorn.conf.py`: production server settings (bind from `PORT`, `WEB_CONCURRENCY` workers).
- `tests/`: pytest; `conftest.py` has `make_app` (fixed config, sequential request IDs) and `client`.
- `ci/Dockerfile`: uv build stage, then distroless Python, non-root, base images pinned by digest.
- `.github/workflows/commit.yml`: CI (see below). `.github/dependabot.yml`: uv, actions, docker.
- `.buildkite/`: Buildkite trial pipeline (`pipeline.yml`), the image it runs in (`Dockerfile`) and
  `in-uv.sh`, which runs a command in that image.

## CI

`.github/workflows/commit.yml` runs on PRs and pushes to `main`. Each job is a `make` target:
`lint` (lock-check, ruff, mypy --strict, actionlint), `format`, `unit-tests` (pytest on Python
3.11–3.14), `coverage` (branch coverage, fails under `fail_under` in `pyproject.toml`), `bandit`,
`audit` (pip-audit on the locked dependencies) and `build-image` (builds the image, smoke-tests
it read-only as non-root, and pushes to GHCR only from `main`). CodeQL runs through GitHub's
default setup.

`.buildkite/pipeline.yml` runs the same targets on Buildkite's hosted Linux agents, as a trial: a
`checks` step (lock-check, fmt-check, lint, typecheck, security, audit, actionlint) and a `tests`
step (coverage, then every supported Python). Both run inside `.buildkite/Dockerfile` through
`.buildkite/in-uv.sh`; `.buildkite/in-uv.sh make check` reproduces them locally with Docker. Keep
the two pipelines' targets in step until the GitHub jobs are removed.

## Conventions

- Typing: `mypy --strict` over `src` and `tests`. No untyped defs; prefer `from __future__ import
  annotations`.
- Lint rules and their reasons are in `[tool.ruff.lint]`. A `# noqa` needs a comment saying why.
- Tests: one file per module (`tests/test_<module>.py`), names that state the behaviour, and a
  test that fails without the change. Coverage must stay at or above the threshold; don't lower it.
- Comments only where the *why* is not obvious from the code.
- New GitHub Actions are pinned by full commit SHA with a version comment
  (`uses: owner/action@<sha> # v1.2.3`); workflows that run PR code use `pull_request`, never
  `pull_request_target`.
- Supported Pythons: `requires-python` in `pyproject.toml`, the `unit-tests` matrix and `PYTHONS`
  in the Makefile move together. `.python-version` (3.13) matches the Docker image's Python.
