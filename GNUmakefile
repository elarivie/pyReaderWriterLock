#!/usr/bin/env -S make -f

# This MakeFile provides development shortcut to frequent tasks.

SHELL=/bin/sh

# To be reproducible
export PYTHONHASHSEED=0
export PYTHONIOENCODING=utf-8
export PYTHONDONTWRITEBYTECODE=""
export TZ=UTC
export LANGUAGE=en_US
export LC_ALL=C.UTF-8
export SOURCE_DATE_EPOCH=0

# List of tool used within current file.
CAT=cat
CUT=cut
DATE=date
ECHO=echo
FIND=find
GIT=git
GREP=grep
GZIP=gzip
MV=mv
PYTHON=python3
RM=rm
RM_RF=$(RM) -rf
SED=sed
SORT=sort
TAR=tar
UNIQ=uniq

# Define some dynamic variables
THENAME:=$(shell $(CAT) NAME)
THEVERSION:=$(shell $(CAT) VERSION)
THEHEARTBEAT=$(shell $(CAT) HEARTBEAT)
# THENAME:=$(file < NAME) ⸻ Uncomment once travisCI will offer GNU Make 4.0
# THEVERSION:=$(file < VERSION) ⸻ Uncomment once travisCI will offer GNU Make 4.0
# THEHEARTBEAT=$(file < HEARTBEAT) ⸻ Uncomment once travisCI will offer GNU Make 4.0

# Use the HEARTBEAT as the SOURCE_DATE
SOURCE_DATE="$(THEHEARTBEAT)-01 00:00:00Z"
export SOURCE_DATE_EPOCH=$(shell $(DATE) --date $(SOURCE_DATE) +%s)

SRC_FILES = $(shell $(FIND) ./ -path ./build -prune -o -type f -name '*.py' -print)

.PHONY: all
all: check.lint check.test.coverage.report check.test.coverage	## Build the project

.PHONY: check.lint.dist
check.lint.dist: dist	## Lint distribution files
	$(PYTHON) "-m" "twine" check dist/*

.PHONY: check.lint
check.lint: check.lint.dist check.lint.flake8 check.lint.mypy check.lint.pydocstyle check.lint.pylint	## Lint with all lint tool

.PHONY: check.lint.flake8
check.lint.flake8:	## Lint with flake8
	$(PYTHON) "-m" "flake8" "--show-source" "--config" "setup.cfg" $(SRC_FILES)

.PHONY: check.lint.mypy
check.lint.mypy:	## Lint with mypy
	$(PYTHON) "-m" "mypy" "--config-file" "setup.cfg" "--show-column-numbers" "--show-error-context" "--show-error-codes" "--pretty" $(SRC_FILES)

.PHONY: check.lint.pydocstyle
check.lint.pydocstyle:	## Lint with pydocstyle
	$(PYTHON) "-m" "pydocstyle" "--config" "setup.cfg" "--explain" "--source" $(SRC_FILES)

.PHONY: check.lint.pylint
check.lint.pylint:	## Lint with pylint
	$(PYTHON) "-m" "pylint" "--persistent" "n" "--rcfile" "setup.cfg" $(SRC_FILES)

.coverage: export COVERAGE_FILE=.coverage~
.coverage: $(SRC_FILES)
	$(RM_RF) ".coverage"
	$(RM_RF) ".coverage~"
	$(PYTHON) "-m" "coverage" "run" "--branch" "--omit=setup.py" "--source" . "-m" "unittest" "discover" "-s" "tests/"
	$(MV) ".coverage~" ".coverage"

htmlcov: .coverage
	$(RM_RF) "htmlcov"
	$(RM_RF) "htmlcov~"
	$(PYTHON) "-m" "coverage" "html" "--directory" "htmlcov~"
	$(MV) "htmlcov~" "htmlcov"

.PHONY: check.test
check.test:	## Run unit tests
	export PYTHONPATH=.; $(PYTHON) "-m" "unittest" "discover" "-s" "tests/"

.PHONY: check.test.coverage
check.test.coverage: .coverage	## Display code coverage of tests
	$(PYTHON) "-m" "coverage" "report"

.PHONY: check.test.coverage.report
check.test.coverage.report: htmlcov	## Generate code coverage html report

.PHONY: AUTHORS.md
AUTHORS.md:
	$(ECHO) "Author\n======\nÉric Larivière <ericlariviere@hotmail.com>\n\nContributors\n============\n\n**Thank you to every contributor**\n\n" > ./AUTHORS.md~
	- $(GIT) log --raw | $(GREP) "^Author: " | $(GREP) -v ".noreply.github" | $(SORT) | $(UNIQ) -i | $(CUT) -d ' ' -f2- | $(SED) 's/^/- /' >> "./AUTHORS.md~"
	$(MV) "./AUTHORS.md~" "./AUTHORS.md"
	- $(GIT) add AUTHORS.md

.PHONY: HEARTBEAT
HEARTBEAT:
	$(RM_RF) "./HEARTBEAT"
	$(DATE) --utc +%Y-%m > "./HEARTBEAT~"
	$(MV) "./HEARTBEAT~" "./HEARTBEAT"
	- $(GIT) add HEARTBEAT

.PHONY: gitcommit
gitcommit: AUTHORS.md HEARTBEAT
	- $(GIT) commit

dist: HEARTBEAT MANIFEST.in NAME README.md VERSION setup.cfg $(SRC_FILES)	## Build distribution folder
	$(RM_RF) "dist"
	$(RM_RF) "dist~"
	$(PYTHON) setup.py sdist --dist-dir dist~ --formats=tar

	# Redo generated source tar file but this time in a reproducible way
	cd "dist~/"; $(TAR) --extract -f "$(THENAME)-$(THEVERSION).tar"
	$(RM) "dist~/$(THENAME)-$(THEVERSION).tar"
	$(TAR)\
		--create\
		--format=posix \
		--pax-option=exthdr.name=%d/PaxHeaders/%f,delete=atime,delete=ctime,delete=mtime \
		--mtime=$(SOURCE_DATE) \
		--sort=name \
		--numeric-owner \
		--owner=0 \
		--group=0 \
		--mode=go-rwx,u+rw,a-s \
		--file - \
		--directory=dist~/ \
		"$(THENAME)-$(THEVERSION)" \
		| $(GZIP)\
		--no-name\
		--best\
		--stdout \
	> "dist~/$(THENAME)-$(THEVERSION).tar.gz"
	$(RM_RF) "dist~/$(THENAME)-$(THEVERSION)"

	$(PYTHON) setup.py bdist_wheel --dist-dir dist~
	$(MV) "dist~" "dist"

.PHONY: publish
publish: dist	## Publish a new version to pypi
	#https://pypi.org/project/readerwriterlock
	$(PYTHON) "-m" "twine" upload dist/*

.PHONY: publish-test
publish-test: dist
	#https://test.pypi.org/project/readerwriterlock
	$(PYTHON) "-m" "twine" upload --repository-url https://test.pypi.org/legacy/ dist/*

	#To install:
	#  python3 -m pip install -U --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple readerwriterlock

.PHONY: clean
clean:	## Clean the project folder
	# Manually
	$(RM_RF) .coverage
	$(RM_RF) .mypy_cache/
	$(RM_RF) build/
	$(RM_RF) dist/
	$(RM_RF) htmlcov/
	$(RM_RF) readerwriterlock.egg-info/
	# Automatically (If working from a git repository)
	- $(GIT) clean --force -x -d

.PHONY: help
help:	## Show the list of available targets
	@ $(GREP) -E '^[a-zA-Z_0-9\.-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}';

.DEFAULT_GOAL := help
.DELETE_ON_ERROR:
