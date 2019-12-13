#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read Write Lock."""

import threading
import time

from typing import Callable
from typing import Optional
from typing import Type
from types import TracebackType
from typing_extensions import Protocol


class Lockable(Protocol):
	"""Lockable.  Compatible with threading.Lock interface."""

	def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
		"""Acquire a lock."""
		...

	def release(self) -> None:
		"""Release the lock."""

	def locked(self) -> bool:
		"""Answer to 'is it currently locked?'."""
		return False  # Will be overriden.  # pragma: no cover

	def __enter__(self) -> bool:
		"""Enter context manager."""
		self.acquire()
		return False

	def __exit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[Exception], exc_tb: Optional[TracebackType]) -> Optional[bool]:  # type: ignore
		"""Exit context manager."""
		self.release()
		return False


class RWLockable(Protocol):
	"""Read/write lock."""

	def gen_rlock(self) -> Lockable:
		"""Generate a reader lock."""

	def gen_wlock(self) -> Lockable:
		"""Generate a writer lock."""


class RWLockRead(RWLockable):
	"""A Read/Write lock giving preference to Reader."""

	def __init__(self, lock_factory: Callable[[], Lockable] = lambda: threading.Lock()) -> None:
		"""Init."""
		self.v_read_count = 0
		self.c_resource = lock_factory()
		self.c_lock_read_count = lock_factory()
		super().__init__()

	class _aReader(Lockable):
		def __init__(self, p_RWLock: "RWLockRead") -> None:
			self.c_rw_lock = p_RWLock
			self.v_locked = False
			super().__init__()

		def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
			"""Acquire a lock."""
			p_timeout = None if (blocking and timeout < 0) else (timeout if blocking else 0)
			c_deadline = None if p_timeout is None else (time.time() + p_timeout)
			if not self.c_rw_lock.c_lock_read_count.acquire(blocking=True, timeout=-1 if c_deadline is None else max(0, c_deadline - time.time())):
				return False
			self.c_rw_lock.v_read_count += 1
			if 1 == self.c_rw_lock.v_read_count:
				if not self.c_rw_lock.c_resource.acquire(blocking=True, timeout=-1 if c_deadline is None else max(0, c_deadline - time.time())):
					self.c_rw_lock.v_read_count -= 1
					self.c_rw_lock.c_lock_read_count.release()
					return False
			self.c_rw_lock.c_lock_read_count.release()
			self.v_locked = True
			return True

		def release(self) -> None:
			"""Release the lock."""
			if not self.v_locked: raise RuntimeError("cannot release un-acquired lock")
			self.v_locked = False
			self.c_rw_lock.c_lock_read_count.acquire()
			self.c_rw_lock.v_read_count -= 1
			if 0 == self.c_rw_lock.v_read_count:
				self.c_rw_lock.c_resource.release()
			self.c_rw_lock.c_lock_read_count.release()

		def locked(self) -> bool:
			"""Answer to 'is it currently locked?'."""
			return self.v_locked

	class _aWriter(Lockable):
		def __init__(self, p_RWLock: "RWLockRead") -> None:
			self.c_rw_lock = p_RWLock
			self.v_locked = False
			super().__init__()

		def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
			"""Acquire a lock."""
			self.v_locked = self.c_rw_lock.c_resource.acquire(blocking, timeout)
			return self.v_locked

		def release(self) -> None:
			"""Release the lock."""
			if not self.v_locked: raise RuntimeError("cannot release un-acquired lock")
			self.v_locked = False
			self.c_rw_lock.c_resource.release()

		def locked(self) -> bool:
			"""Answer to 'is it currently locked?'."""
			return self.v_locked

	def gen_rlock(self) -> "RWLockRead._aReader":
		"""Generate a reader lock."""
		return RWLockRead._aReader(self)

	def gen_wlock(self) -> "RWLockRead._aWriter":
		"""Generate a writer lock."""
		return RWLockRead._aWriter(self)


class RWLockWrite(RWLockable):
	"""A Read/Write lock giving preference to Writer."""

	def __init__(self, lock_factory: Callable[[], Lockable] = lambda: threading.Lock()) -> None:
		"""Init."""
		self.v_read_count = 0
		self.v_write_count = 0
		self.c_lock_read_count = lock_factory()
		self.c_lock_write_count = lock_factory()
		self.c_lock_read_entry = lock_factory()
		self.c_lock_read_try = lock_factory()
		self.c_resource = lock_factory()
		super().__init__()

	class _aReader(Lockable):
		def __init__(self, p_RWLock: "RWLockWrite") -> None:
			self.c_rw_lock = p_RWLock
			self.v_locked = False
			super().__init__()

		def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
			"""Acquire a lock."""
			p_timeout = None if (blocking and timeout < 0) else (timeout if blocking else 0)
			c_deadline = None if p_timeout is None else (time.time() + p_timeout)
			if not self.c_rw_lock.c_lock_read_entry.acquire(blocking=True, timeout=-1 if c_deadline is None else max(0, c_deadline - time.time())):
				return False
			if not self.c_rw_lock.c_lock_read_try.acquire(blocking=True, timeout=-1 if c_deadline is None else max(0, c_deadline - time.time())):
				self.c_rw_lock.c_lock_read_entry.release()
				return False
			if not self.c_rw_lock.c_lock_read_count.acquire(blocking=True, timeout=-1 if c_deadline is None else max(0, c_deadline - time.time())):
				self.c_rw_lock.c_lock_read_try.release()
				self.c_rw_lock.c_lock_read_entry.release()
				return False
			self.c_rw_lock.v_read_count += 1
			if 1 == self.c_rw_lock.v_read_count:
				if not self.c_rw_lock.c_resource.acquire(blocking=True, timeout=-1 if c_deadline is None else max(0, c_deadline - time.time())):
					self.c_rw_lock.c_lock_read_try.release()
					self.c_rw_lock.c_lock_read_entry.release()
					self.c_rw_lock.v_read_count -= 1
					self.c_rw_lock.c_lock_read_count.release()
					return False
			self.c_rw_lock.c_lock_read_count.release()
			self.c_rw_lock.c_lock_read_try.release()
			self.c_rw_lock.c_lock_read_entry.release()
			self.v_locked = True
			return True

		def release(self) -> None:
			"""Release the lock."""
			if not self.v_locked: raise RuntimeError("cannot release un-acquired lock")
			self.v_locked = False
			self.c_rw_lock.c_lock_read_count.acquire()
			self.c_rw_lock.v_read_count -= 1
			if 0 == self.c_rw_lock.v_read_count:
				self.c_rw_lock.c_resource.release()
			self.c_rw_lock.c_lock_read_count.release()

		def locked(self) -> bool:
			"""Answer to 'is it currently locked?'."""
			return self.v_locked

	class _aWriter(Lockable):
		def __init__(self, p_RWLock: "RWLockWrite") -> None:
			self.c_rw_lock = p_RWLock
			self.v_locked = False
			super().__init__()

		def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
			"""Acquire a lock."""
			p_timeout = None if (blocking and timeout < 0) else (timeout if blocking else 0)
			c_deadline = None if p_timeout is None else (time.time() + p_timeout)
			if not self.c_rw_lock.c_lock_write_count.acquire(blocking=True, timeout=-1 if c_deadline is None else max(0, c_deadline - time.time())):
				return False
			self.c_rw_lock.v_write_count += 1
			if 1 == self.c_rw_lock.v_write_count:
				if not self.c_rw_lock.c_lock_read_try.acquire(blocking=True, timeout=-1 if c_deadline is None else max(0, c_deadline - time.time())):
					self.c_rw_lock.v_write_count -= 1
					self.c_rw_lock.c_lock_write_count.release()
					return False
			self.c_rw_lock.c_lock_write_count.release()
			if not self.c_rw_lock.c_resource.acquire(blocking=True, timeout=-1 if c_deadline is None else max(0, c_deadline - time.time())):
				self.c_rw_lock.c_lock_write_count.acquire()
				self.c_rw_lock.v_write_count -= 1
				if 0 == self.c_rw_lock.v_write_count:
					self.c_rw_lock.c_lock_read_try.release()
				self.c_rw_lock.c_lock_write_count.release()
				return False
			self.v_locked = True
			return True

		def release(self) -> None:
			"""Release the lock."""
			if not self.v_locked: raise RuntimeError("cannot release un-acquired lock")
			self.v_locked = False
			self.c_rw_lock.c_resource.release()
			self.c_rw_lock.c_lock_write_count.acquire()
			self.c_rw_lock.v_write_count -= 1
			if 0 == self.c_rw_lock.v_write_count:
				self.c_rw_lock.c_lock_read_try.release()
			self.c_rw_lock.c_lock_write_count.release()

		def locked(self) -> bool:
			"""Answer to 'is it currently locked?'."""
			return self.v_locked

	def gen_rlock(self) -> "RWLockWrite._aReader":
		"""Generate a reader lock."""
		return RWLockWrite._aReader(self)

	def gen_wlock(self) -> "RWLockWrite._aWriter":
		"""Generate a writer lock."""
		return RWLockWrite._aWriter(self)


class RWLockFair(RWLockable):
	"""A Read/Write lock giving fairness to both Reader and Writer."""

	def __init__(self, lock_factory: Callable[[], Lockable] = threading.Lock) -> None:
		"""Init."""
		self.v_read_count = 0
		self.c_lock_read_count = lock_factory()
		self.c_lock_read = lock_factory()
		self.c_lock_write = lock_factory()
		super().__init__()

	class _aReader(Lockable):
		def __init__(self, p_RWLock: "RWLockFair") -> None:
			self.c_rw_lock = p_RWLock
			self.v_locked = False
			super().__init__()

		def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
			"""Acquire a lock."""
			p_timeout = None if (blocking and timeout < 0) else (timeout if blocking else 0)
			c_deadline = None if p_timeout is None else (time.time() + p_timeout)
			if not self.c_rw_lock.c_lock_read.acquire(blocking=True, timeout=-1 if c_deadline is None else max(0, c_deadline - time.time())):
				return False
			if not self.c_rw_lock.c_lock_read_count.acquire(blocking=True, timeout=-1 if c_deadline is None else max(0, c_deadline - time.time())):
				self.c_rw_lock.c_lock_read.release()
				return False
			self.c_rw_lock.v_read_count += 1
			if 1 == self.c_rw_lock.v_read_count:
				if not self.c_rw_lock.c_lock_write.acquire(blocking=True, timeout=-1 if c_deadline is None else max(0, c_deadline - time.time())):
					self.c_rw_lock.v_read_count -= 1
					self.c_rw_lock.c_lock_read_count.release()
					self.c_rw_lock.c_lock_read.release()
					return False
			self.c_rw_lock.c_lock_read_count.release()
			self.c_rw_lock.c_lock_read.release()
			self.v_locked = True
			return True

		def release(self) -> None:
			"""Release the lock."""
			if not self.v_locked: raise RuntimeError("cannot release un-acquired lock")
			self.v_locked = False
			self.c_rw_lock.c_lock_read_count.acquire()
			self.c_rw_lock.v_read_count -= 1
			if 0 == self.c_rw_lock.v_read_count:
				self.c_rw_lock.c_lock_write.release()
			self.c_rw_lock.c_lock_read_count.release()

		def locked(self) -> bool:
			"""Answer to 'is it currently locked?'."""
			return self.v_locked

	class _aWriter(Lockable):
		def __init__(self, p_RWLock: "RWLockFair") -> None:
			self.c_rw_lock = p_RWLock
			self.v_locked = False
			super().__init__()

		def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
			"""Acquire a lock."""
			p_timeout = None if (blocking and timeout < 0) else (timeout if blocking else 0)
			c_deadline = None if p_timeout is None else (time.time() + p_timeout)
			if not self.c_rw_lock.c_lock_read.acquire(blocking=True, timeout=-1 if c_deadline is None else max(0, c_deadline - time.time())):
				return False
			if not self.c_rw_lock.c_lock_write.acquire(blocking=True, timeout=-1 if c_deadline is None else max(0, c_deadline - time.time())):
				self.c_rw_lock.c_lock_read.release()
				return False
			self.v_locked = True
			return True

		def release(self) -> None:
			"""Release the lock."""
			if not self.v_locked: raise RuntimeError("cannot release un-acquired lock")
			self.v_locked = False
			self.c_rw_lock.c_lock_write.release()
			self.c_rw_lock.c_lock_read.release()

		def locked(self) -> bool:
			"""Answer to 'is it currently locked?'."""
			return self.v_locked

	def gen_rlock(self) -> "RWLockFair._aReader":
		"""Generate a reader lock."""
		return RWLockFair._aReader(self)

	def gen_wlock(self) -> "RWLockFair._aWriter":
		"""Generate a writer lock."""
		return RWLockFair._aWriter(self)
