# Python Tools Sample

[![CircleCI](https://circleci.com/gh/kaeawc/python-tools-sample/tree/master.svg?style=svg)](https://circleci.com/gh/kaeawc/python-tools-sample/tree/master)

[![codecov](https://codecov.io/gh/kaeawc/python-tools-sample/branch/master/graph/badge.svg)](https://codecov.io/gh/kaeawc/python-tools-sample)

This is a repository of how to use code analysis with continuous integration services to show that the code being written adheres to team code style and tests passing. The goal of these tools is to minimize or reduce tech debt while providing automated checks so that developers can focus on harder and more interesting problems.

# Getting setup

To get started you should create a virtual environment.

```bash
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

# Running code analysis locally

We have a `Makefile` that allows you to do lint, unit test, and coverage reporting on the sample codebase.

```bash
(venv) ~/kaeawc/python-tools-sample (master ✔) ᐅ make
rm -f find test-reports/pycodestyle.log
pycodestyle sample | tee test-reports/pycodestyle.log
find test-reports/pycodestyle.log
test-reports/pycodestyle.log
rm -rf htmlcov
rm -f test-reports/junit-results.xml
rm -f .coverage
nose2 -c unittest.cfg
.
----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
find test-reports/junit-results.xml
test-reports/junit-results.xml
```

# [CircleCI](https://circleci.com/gh/kaeawc/python-tools-sample)

CircleCI currently does checks on every commit to kick off lint, unit test, and coverage reporting.

You can see how CircleCI runs its jobs by following along in the [.circleci/config.yml](https://github.com/kaeawc/python-tools-sample/blob/master/.circleci/config.yml).

# [CodeCov](https://codecov.io/gh/kaeawc/python-tools-sample)

This is a web service that shows how coverage is changing per commit in both lines and complexity. It comments on pull requests about how the changes are effecting overall codebase coverage and where the biggest impacts are.
