Reader Writer Lock
==================

**A python implementation of the three Reader-Writer problems.**

[![repo status Active](https://www.repostatus.org/badges/latest/active.svg "repo status Active")](https://www.repostatus.org/#active)
[![Build Status](https://travis-ci.org/elarivie/pyReaderWriterLock.svg?branch=master)](https://travis-ci.org/elarivie/pyReaderWriterLock)
[![Coverage Status](https://codecov.io/gh/elarivie/pyreaderwriterlock/branch/master/graph/badge.svg)](https://codecov.io/gh/elarivie/pyreaderwriterlock)
[![BugTracker](https://img.shields.io/github/issues/elarivie/pyReaderWriterLock.svg)][pyReaderWriterLock_BugTracker]


[![Python Version](https://img.shields.io/pypi/pyversions/readerwriterlock.svg)][python]
[![Pypi Version](https://img.shields.io/pypi/v/readerwriterlock.svg)][pyReaderWriterLock_Pypi]

[![Code size in bytes](https://img.shields.io/github/languages/code-size/elarivie/pyReaderWriterLock.svg)][pyReaderWriterLock_repo]
[![License](https://img.shields.io/pypi/l/readerwriterlock.svg)][pyReaderWriterLock_License]

[![Downloads](https://pepy.tech/badge/readerwriterlock)](https://pepy.tech/project/readerwriterlock)
[![Downloads](https://pepy.tech/badge/readerwriterlock/month)](https://pepy.tech/project/readerwriterlock/month)
[![Downloads](https://pepy.tech/badge/readerwriterlock/week)](https://pepy.tech/project/readerwriterlock/week)
[![pyReaderWriterLock_repo_star](https://img.shields.io/github/stars/elarivie/pyReaderWriterLock.svg?style=social&label=Stars)][pyReaderWriterLock_repo_star]

Not only does it implement the reader-writer problems, it is also compliant with the python [lock interface](https://docs.python.org/3/library/threading.html#threading.Lock) which among others include support for timeout.

For reading about the theory behind the reader-writer problems refer to [Wikipedia](https://wikipedia.org/wiki/Readers–writers_problem).

# Installation

Install the python package [readerwriterlock](https://pypi.python.org/pypi/readerwriterlock)

```bash
python3 -m pip install -U readerwriterlock
```

# Usage

Initialize a new lock base on your access priority need which is going to be use by the threads:

**Reader priority** (*aka First readers-writers problem*)

```python
from readerwriterlock import rwlock
a = rwlock.RWLockRead()
```

**Writer priority** (*aka Second readers-writers problem*)

```python
from readerwriterlock import rwlock
a = rwlock.RWLockWrite()
```

**Fair priority** (*aka Third readers-writers problem*)

```python
from readerwriterlock import rwlock
a = rwlock.RWLockFair()
```

## Pythonic usage example

```python
with a.gen_rlock():
  #Read stuff

with a.gen_wlock():
  #Write stuff
```

## Use case (Timeout) example
```python
b = a.gen_wlock()
if b.acquire(blocking=True, timeout=5):
  try:
    #Do stuff
  finally:
    b.release()
```

## Live example
Refer to the file [test_rwlock.py](tests/test_rwlock.py) which has above 90% line coverage of [rwlock.py](readerwriterlock/rwlock.py).

The tests can be initiated by doing

```bash
make check.test.coverage
```

Contact
----
* Project: [GitHub](https://github.com/elarivie/pyReaderWriterLock)
* Éric Larivière <ericlariviere@hotmail.com>


[python]: https://www.python.org
[pyReaderWriterLock_repo]: https://github.com/elarivie/pyReaderWriterLock
[pyReaderWriterLock_BugTracker]: https://github.com/elarivie/pyReaderWriterLock/issues
[pyReaderWriterLock_repo_star]: https://github.com/elarivie/pyReaderWriterLock/stargazers
[pyReaderWriterLock_Pypi]: https://pypi.python.org/pypi/readerwriterlock
[pyReaderWriterLock_License]: https://github.com/elarivie/pyReaderWriterLock/blob/master/LICENSE.txt
