Reader Writer Lock
==================

**A python implementation of the three Reader-Writer problems.**

[![Build Status](https://travis-ci.org/elarivie/pyReaderWriterLock.svg?branch=master)](https://travis-ci.org/elarivie/pyReaderWriterLock)
[![BugTracker](https://img.shields.io/github/issues/elarivie/pyReaderWriterLock.svg)][pyReaderWriterLock_BugTracker]
[![pyReaderWriterLock_repo_star](https://img.shields.io/github/stars/elarivie/pyReaderWriterLock.svg?style=social&label=Stars)][pyReaderWriterLock_repo_star]

[![Python Version](https://img.shields.io/pypi/pyversions/readerwriterlock.svg)][python]
[![Pypi Version](https://img.shields.io/pypi/v/readerwriterlock.svg)][pyReaderWriterLock_Pypi]

[![Code size in bytes](https://img.shields.io/github/languages/code-size/elarivie/pyReaderWriterLock.svg)][pyReaderWriterLock_repo]
[![License](https://img.shields.io/pypi/l/readerwriterlock.svg)][pyReaderWriterLock_License]

Not only does it implement the reader-writer problems, it is also compliant with the python lock interface which includes support for timeouts.

For reading about the theory behind the reader-writer problems refer to [Wikipedia](https://wikipedia.org/wiki/Readers–writers_problem).

# Installation

Install the python package [readerwriterlock](https://pypi.python.org/pypi/readerwriterlock)

	python3 -m pip install readerwriterlock


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

```
with a.gen_rlock():
	#Read stuff
with a.gen_wlock():
	#Write stuff
```

## Advanced Usage example
```
b = a.gen_wlock()
if b.acquire(blocking=True, timeout=5):
	#Do stuff
	b.release()
```

## Live example
Refer to the file [rwlock_test.py](tests/rwlock_test.py) which can be directly called, it has above 90% line coverage of [rwlock.py](readerwriterlock/rwlock.py).

The tests can be initiated by doing

```bash
./rwlock_test.py
```

# Build
This project uses the [BUILDME](https://github.com/elarivie/BUILDME) interface, you may therefore build the project by simply doing:
```bash
./BUILDME
```

Contribute
----
You are the welcome to contribute (Welcome in the open source world):
* Bug/Suggestion/Comment

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
