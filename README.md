pyReaderWriterLock
==================

**A python implementation of the three Reader-Writer problems.**

Not only does it implement the reader-writer problems, it is also compliant with the python lock interface which includes support for timeouts.

For reading about the theory behind the reader-writer problems refer to [Wikipedia](https://wikipedia.org/wiki/Readers–writers_problem).

# Usage

1. First initialize a new lock base on your access priority need:

**Reader priority** (*aka First readers-writers problem*)

```python
import RWLock
a = RWLock.RWLockRead()
```

**Writer priority** (*aka Second readers-writers problem*)

```python
import RWLock
a = RWLock.RWLockWrite()
```

**Fair priority** (*aka Third readers-writers problem*)

```python
import RWLock
a = RWLock.RWLockFair()
```

2. Use it in multiple threads:

## Pythonic usage example

```
with a.genRlock():
	#Read stuff
with a.genWlock():
	#Write stuff
```

## Advanced Usage example
```
b = a.genWlock()
if b.acquire(blocking=1, timeout=5):
	#Do stuff
	b.release()
```

## Live example
Refer to the file [RWLock_Test.py](src/RWLock_Test.py) which can be directly called, it has above 90% line coverage of [RWLock.py](src/RWLock.py).

The tests can be initiated by doing

```bash
./RWLock_Test.py
```

# Build
This project use the [BUILDME](https://github.com/elarivie/BUILDME) interface, you may therefore build the project by simply doing:
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

