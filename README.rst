Reader Writer Lock
==================

**A python implementation of the three Reader-Writer problems.**

Not only does it implement the reader-writer problems, it is also compliant with the python lock interface which includes support for timeouts.

For reading about the theory behind the reader-writer problems refer to `Wikipedia <https://wikipedia.org/wiki/Readers–writers_problem>`_.

Installation
------------

Install the `python <https://www.python.org>`_ package `readerwriterlock <https://pypi.python.org/pypi/readerwriterlock/>`_

  python3 -m pip install -U readerwriterlock


Usage
-----

Initialize a new lock base on your access priority need which is going to be use by the threads:

**Reader priority** (*aka First readers-writers problem*)

::

  from readerwriterlock import rwlock
  a = rwlock.RWLockRead()

**Writer priority** (*aka Second readers-writers problem*)

::

  from readerwriterlock import rwlock
  a = rwlock.RWLockWrite()

**Fair priority** (*aka Third readers-writers problem*)

::

  from readerwriterlock import rwlock
  a = rwlock.RWLockFair()

Pythonic usage example
----------------------

::

  with a.gen_rlock():
  	#Read stuff
  with a.gen_wlock():
  	#Write stuff

Advanced Usage example
----------------------

::

  b = a.gen_wlock()
  if b.acquire(blocking=True, timeout=5):
  	#Do stuff
  	b.release()

Live example
------------

Refer to the file `rwlock_test.py <https://github.com/elarivie/pyReaderWriterLock/blob/master/tests/rwlock_test.py>`_ which can be directly called, it has above 90% line coverage of `rwlock.py <https://github.com/elarivie/pyReaderWriterLock/blob/master/readerwriterlock/rwlock.py>`_.

The tests can be initiated by doing

::

  ./rwlock_test.py

Build
-----

This project use the `BUILDME <https://github.com/elarivie/BUILDME>`_ interface, you may therefore build the project by simply doing:

::

  ./BUILDME

Contribute
----------

You are the welcome to contribute.

Contact
-------

:Project: `https://github.com/elarivie/pyReaderWriterLock <https://github.com/elarivie/pyReaderWriterLock>`_
:Bug tracker: `https://github.com/elarivie/pyReaderWriterLock/issues <https://github.com/elarivie/pyReaderWriterLock/issues>`_
:Author: Éric Larivière `ericlariviere@hotmail.com <ericlariviere@hotmail.com>`_
