# Contributing

Thanks for helping out. This file covers the workflow; the [README](README.md) covers the layout,
and [AGENTS.md](AGENTS.md) holds the working rules (for people and coding agents alike).

## Setup

All you need is [uv](https://docs.astral.sh/uv/). `make sync` installs the Python version from
`.python-version`, the app and every dev tool from `uv.lock`. Docker is only needed for
`make docker`.

## Before you push

```bash
make check     # lock-check, format check, ruff, mypy --strict, tests with coverage gate
```

`make check` should pass on every commit you push. `make ci` adds bandit, pip-audit, actionlint and
the tests on every supported Python. Other useful targets:

- `make fmt`: format with ruff (CI fails on a diff).
- `make lint-fix`: apply ruff's automatic fixes.
- `uv run pytest tests/test_config.py -k port`: one test while you iterate.
- `make help`: everything else.

Add tests that fail without your change, and keep coverage at or above the threshold in
`pyproject.toml`. Keep functions simple enough for ruff's complexity limit (10).

## Dependencies

- `uv add <pkg>` for a runtime dependency, `uv add --dev <pkg>` for a tool. Both update `uv.lock`;
  commit it.
- `uv lock --upgrade` refreshes everything; `uv lock --upgrade-package <pkg>` one package.
- Dependabot opens weekly PRs for uv, GitHub Actions and the Docker base images.

## Commits and pull requests

- Imperative subject under about 72 characters (`Add readiness check for the database`), with a
  body when the reason isn't obvious from the diff.
- Branch from `main` and open the PR against `main`. PRs are squash-merged, so the title becomes
  the commit subject.
- Fill in the [PR template](.github/pull_request_template.md). All `commit.yml` jobs must pass.
- Pin new GitHub Actions to a full commit SHA with the version in a comment
  (`uses: owner/action@<sha> # v1.2.3`), and run `make actionlint` after editing a workflow.

## Reporting bugs and requesting features

Use the [issue forms](.github/ISSUE_TEMPLATE). For security vulnerabilities, don't open a public
issue: see [SECURITY.md](SECURITY.md).
