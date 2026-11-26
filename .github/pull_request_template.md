<!-- The title becomes the squash-merge commit subject: imperative, under ~72 chars. -->

## What and why

<!-- What does this change, and why? Link the issue: "Closes #123". -->

## How it was verified

<!-- Commands you ran and what you saw. -->

## Checklist

- [ ] `make check` passes (lock-check, format, ruff, mypy, tests with coverage gate)
- [ ] Tests added or updated, and they fail without this change
- [ ] No new bandit or pip-audit findings (`make ci`)
- [ ] Docs updated (README, `AGENTS.md`, `CONTRIBUTING.md`) if behaviour, layout, configuration or targets changed
- [ ] Dependencies added with `uv add` and `uv.lock` committed; new actions pinned by SHA
