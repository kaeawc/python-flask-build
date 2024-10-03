# Python Flask Build

Experimental Python build tooling, references, and CI pipeline for a Flask web server. The goal is to showcase best practices as well as be a good foundation for starting out a new Flask project.

# Getting setup

To get started you should create a virtual environment.

```bash
python3 -m venv .venv
.venv/bin/activate
pip install -r requirements.txt
```

# Running code analysis locally

This project uses [tox](https://tox.wiki/) to automate packaging, testing, and release processes.

```bash
(venv) ᐅ tox list
default environments:
py39       -> [no description]
py310      -> [no description]
py311      -> [no description]

additional environments:
lint       -> Run code linting with flake8
format     -> Auto-format code with black
typecheck  -> Auto-format code with mypy
coverage   -> Run tests and check test coverage
monkeytype -> [no description]
```
