#!/usr/bin/make -f -r

# This MakeFile provides development shortcut to frequent tasks.

SHELL=/bin/sh

CUT=cut
GIT=git
GREP=grep
DATE=date
ECHO=echo
MKDIR=mkdir
TOUCH=touch
RM=rm
RM_RF=${RM} -rf
SED=sed
SORT=sort
TAR=tar
UNIQ=uniq

srcdir=.

THENAME :=`cat "${srcdir}/NAME"`
THEVERSION :=`cat "${srcdir}/VERSION"`

all: BUILDME

BUILDME: clean
	${srcdir}/BUILDME

AUTHORS:
	cd ${srcdir}
	${ECHO} "Authors\n=======\nWe'd like to thank the following people for their contributions.\n\n" > ${srcdir}/AUTHORS.md
	${GIT} log --raw | ${GREP} "^Author: " | ${GREP} -v ".noreply.github" | ${SORT} | ${UNIQ} | ${CUT} -d ' ' -f2- | ${SED} 's/^/- /' >> ${srcdir}/AUTHORS.md
	${GIT} add AUTHORS.md

HEARTBEAT:
	cd ${srcdir}
	${DATE} --utc +%Y-%m > ${srcdir}/HEARTBEAT
	${GIT} add HEARTBEAT

gitcommit: clean AUTHORS HEARTBEAT
	cd ${srcdir}
	- ${GIT} commit

dist: clean
	python3 setup.py sdist
	python3 setup.py bdist_wheel

publish: dist
	#https://pypi.org/project/readerwriterlock
	twine upload dist/*

publish-test: dist
	#https://test.pypi.org/project/readerwriterlock
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

	#To install:
	#  pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple readerwriterlock

clean:
	${RM_RF} ${srcdir}/dist
	${RM_RF} ${srcdir}/${THENAME}.egg-info
	${RM_RF} ${srcdir}/.mypy_cache
	${RM_RF} ${srcdir}/build

.PHONY: all BUILDME HEARTBEAT AUTHORS gitcommit dist publish publish-test clean
