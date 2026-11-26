# Developer entry points. `make help` lists targets.
#
# Everything runs through uv: dev tools (ruff, mypy, pytest, bandit, pip-audit, actionlint) are
# pinned in the `dev` dependency group of pyproject.toml and locked in uv.lock, so there is nothing
# to install beyond uv itself. Each CI job in .github/workflows/commit.yml is one of these targets.

UV      ?= uv
RUN     := $(UV) run --locked
IMAGE   ?= python-flask-build:dev
# Python versions CI tests against; `make test-all` runs every one.
PYTHONS ?= 3.11 3.12 3.13 3.14

.DEFAULT_GOAL := help

##@ Develop

.PHONY: sync
sync: ## Install the app and dev tools into .venv from uv.lock
	$(UV) sync --locked

.PHONY: run
run: ## Run the Flask development server (HOST, PORT, DEBUG from the environment)
	$(RUN) python -m python_flask_build

.PHONY: serve
serve: ## Run the production server (gunicorn, configured by gunicorn.conf.py)
	$(RUN) gunicorn

.PHONY: docker
docker: ## Build the container image from ci/Dockerfile
	docker build -f ci/Dockerfile -t $(IMAGE) .

.PHONY: docker-run
docker-run: docker ## Build and run the image on http://localhost:5000
	docker run --rm -p 5000:5000 $(IMAGE)

##@ Test

.PHONY: test
test: ## Run the tests with branch coverage (fails under the threshold in pyproject.toml)
	@mkdir -p reports/junit
	$(RUN) pytest --cov --cov-report=term --cov-report=html --cov-report=xml \
		--junitxml=reports/junit/results.xml

.PHONY: test-all
test-all: ## Run the tests on every supported Python (uv downloads them)
	@for py in $(PYTHONS); do \
		echo "== Python $$py"; \
		$(UV) run --locked --isolated --python $$py pytest -q || exit 1; \
	done

##@ Quality

.PHONY: fmt
fmt: ## Format code and sort imports
	$(RUN) ruff format .
	$(RUN) ruff check --select I --fix .

.PHONY: fmt-check
fmt-check: ## Fail if formatting would change anything
	$(RUN) ruff format --check --diff .

.PHONY: lint
lint: ## Lint with ruff (rules in pyproject.toml)
	$(RUN) ruff check .

.PHONY: lint-fix
lint-fix: ## Apply ruff's automatic fixes
	$(RUN) ruff check --fix .

.PHONY: typecheck
typecheck: ## Type-check src and tests with mypy --strict
	$(RUN) mypy

.PHONY: security
security: ## Static security analysis with bandit
	$(RUN) bandit -c pyproject.toml -r src gunicorn.conf.py

.PHONY: audit
audit: ## Check locked dependencies for known vulnerabilities (pip-audit)
	$(UV) export --locked --no-emit-project --no-hashes --format requirements-txt -o .audit-requirements.txt
	$(RUN) pip-audit --strict --disable-pip --no-deps -r .audit-requirements.txt; \
		status=$$?; rm -f .audit-requirements.txt; exit $$status

.PHONY: actionlint
actionlint: ## Lint GitHub Actions workflows
	$(RUN) actionlint

.PHONY: lock-check
lock-check: ## Fail if uv.lock is out of date with pyproject.toml
	$(UV) lock --check

##@ Aggregates

.PHONY: check
check: lock-check fmt-check lint typecheck test ## Fast pre-push gate

.PHONY: ci
ci: check security audit actionlint test-all ## Everything CI runs except the image build

.PHONY: clean
clean: ## Remove build, test and cache artifacts
	rm -rf reports .coverage .pytest_cache .mypy_cache .ruff_cache dist build

.PHONY: help
help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make \033[36m<target>\033[0m\n"} \
		/^[a-zA-Z_%-]+:.*##/ { printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2 } \
		/^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) }' $(MAKEFILE_LIST)
