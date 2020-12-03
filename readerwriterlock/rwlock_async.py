#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Read Write Lock."""

import asyncio
import sys
import time

from typing import Callable
from typing import Optional
from typing import Type
from types import TracebackType
from typing_extensions import Protocol
from typing_extensions import runtime_checkable

try:
	from asyncio import create_task as run_task
except ImportError:
	from asyncio import ensure_future as run_task

try:
	asyncio.Lock().release()
except BaseException as exc:
	RELEASE_ERR_CLS = type(exc)  # pylint: disable=invalid-name
	RELEASE_ERR_MSG = str(exc)
else:
	raise AssertionError()  # pragma: no cover


@runtime_checkable
class Lockable(Protocol):
	"""Lockable.  Compatible with threading.Lock interface."""

	async def acquire(self) -> bool:
		"""Acquire a lock."""
		raise AssertionError("Should be overriden")  # Will be overriden.  # pragma: no cover

	async def release(self) -> None:
		"""Release the lock."""
		raise AssertionError("Should be overriden")  # Will be overriden.  # pragma: no cover

	async def locked(self) -> bool:
		"""Answer to 'is it currently locked?'."""
		raise AssertionError("Should be overriden")  # Will be overriden.  # pragma: no cover

	async def __aenter__(self) -> bool:
		"""Enter context manager."""
		await self.acquire()
		return False

	async def __aexit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[Exception], exc_tb: Optional[TracebackType]) -> Optional[bool]:  # type: ignore
		"""Exit context manager."""
		await self.release()
		return False


@runtime_checkable
class LockableD(Lockable, Protocol):
	"""Lockable Downgradable."""

	async def downgrade(self) -> Lockable:
		"""Downgrade."""
		raise AssertionError("Should be overriden")  # Will be overriden.  # pragma: no cover


class _ThreadSafeInt():
	"""Internal thread safe integer like object.

	Implements only the bare minimum features for the RWLock implementation's need.
	"""

	def __init__(self, initial_value: int, lock_factory: Callable[[], Lockable] = asyncio.Lock) -> None:
		"""Init."""
		self.__value_lock = lock_factory()
		self.__value: int = initial_value

	def __int__(self) -> int:
		"""Get int value."""
		return self.__value

	def __eq__(self, other) -> bool:
		"""Self == other."""
		return int(self) == other

	async def inc(self):
		async with self.__value_lock:
			self.__value += 1

	async def dec(self):
		async with self.__value_lock:
			self.__value -= 1

	def __iadd__(self, other) -> "_ThreadSafeInt":
		"""Self += other."""
		raise DeprecationWarning("To be removed")

	def __isub__(self, other) -> "_ThreadSafeInt":
		"""Self -= other."""
		raise DeprecationWarning("To be removed")

@runtime_checkable
class RWLockable(Protocol):
	"""Read/write lock."""

	async def gen_rlock(self) -> Lockable:
		"""Generate a reader lock."""
		raise AssertionError("Should be overriden")  # Will be overriden.  # pragma: no cover

	async def gen_wlock(self) -> Lockable:
		"""Generate a writer lock."""
		raise AssertionError("Should be overriden")  # Will be overriden.  # pragma: no cover


@runtime_checkable
class RWLockableD(Protocol):
	"""Read/write lock Downgradable."""

	async def gen_rlock(self) -> Lockable:
		"""Generate a reader lock."""
		raise AssertionError("Should be overriden")  # Will be overriden.  # pragma: no cover

	async def gen_wlock(self) -> LockableD:
		"""Generate a writer lock."""
		raise AssertionError("Should be overriden")  # Will be overriden.  # pragma: no cover


class RWLockRead(RWLockable):
	"""A Read/Write lock giving preference to Reader."""

	def __init__(self, lock_factory: Callable[[], Lockable] = asyncio.Lock, time_source: Callable[[], float] = time.perf_counter) -> None:
		"""Init."""
		self.v_read_count: int = 0
		self.c_time_source = time_source
		self.c_resource = lock_factory()
		self.c_lock_read_count = lock_factory()
		super().__init__()

	class _aReader(Lockable):
		def __init__(self, p_RWLock: "RWLockRead") -> None:
			self.c_rw_lock = p_RWLock
			self.v_locked: bool = False
			super().__init__()

		async def acquire(self) -> bool:
			"""Acquire a lock."""
			if not await self.c_rw_lock.c_lock_read_count.acquire():
				return False
			self.c_rw_lock.v_read_count += 1
			if 1 == self.c_rw_lock.v_read_count:
				if not await self.c_rw_lock.c_resource.acquire():
					self.c_rw_lock.v_read_count -= 1
					self.c_rw_lock.c_lock_read_count.release()
					return False
			self.c_rw_lock.c_lock_read_count.release()
			self.v_locked = True
			return True

		async def release(self) -> None:
			"""Release the lock."""
			if not self.v_locked: raise RELEASE_ERR_CLS(RELEASE_ERR_MSG)
			self.v_locked = False
			await self.c_rw_lock.c_lock_read_count.acquire()
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
			self.v_locked: bool = False
			super().__init__()

		async def acquire(self) -> bool:
			"""Acquire a lock."""
			locked: bool = await self.c_rw_lock.c_resource.acquire()
			self.v_locked = locked
			return locked

		async def release(self) -> None:
			"""Release the lock."""
			if not self.v_locked: raise RELEASE_ERR_CLS(RELEASE_ERR_MSG)
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

	def __init__(self, lock_factory: Callable[[], Lockable] = asyncio.Lock, time_source: Callable[[], float] = time.perf_counter) -> None:
		"""Init."""
		self.v_read_count: int = 0
		self.v_write_count: int = 0
		self.c_time_source = time_source
		self.c_lock_read_count = lock_factory()
		self.c_lock_write_count = lock_factory()
		self.c_lock_read_entry = lock_factory()
		self.c_lock_read_try = lock_factory()
		self.c_resource = lock_factory()
		super().__init__()

	class _aReader(Lockable):
		def __init__(self, p_RWLock: "RWLockWrite") -> None:
			self.c_rw_lock = p_RWLock
			self.v_locked: bool = False
			super().__init__()

		async def acquire(self) -> bool:
			"""Acquire a lock."""
			if not await self.c_rw_lock.c_lock_read_entry.acquire():
				return False
			if not await self.c_rw_lock.c_lock_read_try.acquire():
				self.c_rw_lock.c_lock_read_entry.release()
				return False
			if not await self.c_rw_lock.c_lock_read_count.acquire():
				self.c_rw_lock.c_lock_read_try.release()
				self.c_rw_lock.c_lock_read_entry.release()
				return False
			self.c_rw_lock.v_read_count += 1
			if 1 == self.c_rw_lock.v_read_count:
				if not await self.c_rw_lock.c_resource.acquire():
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

		async def release(self) -> None:
			"""Release the lock."""
			if not self.v_locked: raise RELEASE_ERR_CLS(RELEASE_ERR_MSG)
			self.v_locked = False
			await self.c_rw_lock.c_lock_read_count.acquire()
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
			self.v_locked: bool = False
			super().__init__()

		async def acquire(self) -> bool:
			"""Acquire a lock."""
			if not await self.c_rw_lock.c_lock_write_count.acquire():
				return False
			self.c_rw_lock.v_write_count += 1
			if 1 == int(self.c_rw_lock.v_write_count):
				if not await self.c_rw_lock.c_lock_read_try.acquire():
					self.c_rw_lock.v_write_count -= 1
					self.c_rw_lock.c_lock_write_count.release()
					return False
			self.c_rw_lock.c_lock_write_count.release()
			if not await self.c_rw_lock.c_resource.acquire():
				await self.c_rw_lock.c_lock_write_count.acquire()
				self.c_rw_lock.v_write_count -= 1
				if 0 == int(self.c_rw_lock.v_write_count):
					self.c_rw_lock.c_lock_read_try.release()
				self.c_rw_lock.c_lock_write_count.release()
				return False
			self.v_locked = True
			return True

		async def release(self) -> None:
			"""Release the lock."""
			if not self.v_locked: raise RELEASE_ERR_CLS(RELEASE_ERR_MSG)
			self.v_locked = False
			self.c_rw_lock.c_resource.release()
			await self.c_rw_lock.c_lock_write_count.acquire()
			self.c_rw_lock.v_write_count -= 1
			if 0 == int(self.c_rw_lock.v_write_count):
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

	def __init__(self, lock_factory: Callable[[], Lockable] = asyncio.Lock, time_source: Callable[[], float] = time.perf_counter) -> None:
		"""Init."""
		self.v_read_count: int = 0
		self.c_time_source = time_source
		self.c_lock_read_count = lock_factory()
		self.c_lock_read = lock_factory()
		self.c_lock_write = lock_factory()
		super().__init__()

	class _aReader(Lockable):
		def __init__(self, p_RWLock: "RWLockFair") -> None:
			self.c_rw_lock = p_RWLock
			self.v_locked: bool = False
			super().__init__()

		async def acquire(self) -> bool:
			"""Acquire a lock."""
			if not await self.c_rw_lock.c_lock_read.acquire():
				return False
			if not await self.c_rw_lock.c_lock_read_count.acquire():
				self.c_rw_lock.c_lock_read.release()
				return False
			self.c_rw_lock.v_read_count += 1
			if 1 == self.c_rw_lock.v_read_count:
				if not await self.c_rw_lock.c_lock_write.acquire():
					self.c_rw_lock.v_read_count -= 1
					self.c_rw_lock.c_lock_read_count.release()
					self.c_rw_lock.c_lock_read.release()
					return False
			self.c_rw_lock.c_lock_read_count.release()
			self.c_rw_lock.c_lock_read.release()
			self.v_locked = True
			return True

		async def release(self) -> None:
			"""Release the lock."""
			if not self.v_locked: raise RELEASE_ERR_CLS(RELEASE_ERR_MSG)
			self.v_locked = False
			await self.c_rw_lock.c_lock_read_count.acquire()
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
			self.v_locked: bool = False
			super().__init__()

		async def acquire(self) -> bool:
			"""Acquire a lock."""
			if not await self.c_rw_lock.c_lock_read.acquire():
				return False
			if not await self.c_rw_lock.c_lock_write.acquire():
				self.c_rw_lock.c_lock_read.release()
				return False
			self.v_locked = True
			return True

		async def release(self) -> None:
			"""Release the lock."""
			if not self.v_locked: raise RELEASE_ERR_CLS(RELEASE_ERR_MSG)
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

class RWLockReadD(RWLockableD):
	"""A Read/Write lock giving preference to Reader."""

	def __init__(self, lock_factory: Callable[[], Lockable] = asyncio.Lock, time_source: Callable[[], float] = time.perf_counter) -> None:
		"""Init."""
		self.v_read_count: _ThreadSafeInt = _ThreadSafeInt(initial_value=0, lock_factory=lock_factory)
		self.c_time_source = time_source
		self.c_resource = lock_factory()
		self.c_lock_read_count = lock_factory()
		super().__init__()

	class _aReader(Lockable):
		def __init__(self, p_RWLock: "RWLockReadD") -> None:
			self.c_rw_lock = p_RWLock
			self.v_locked: bool = False
			super().__init__()

		async def acquire(self) -> bool:
			"""Acquire a lock."""
			if not await self.c_rw_lock.c_lock_read_count.acquire():
				return False
			await self.c_rw_lock.v_read_count.inc()
			if 1 == int(self.c_rw_lock.v_read_count):
				if not await self.c_rw_lock.c_resource.acquire():
					await self.c_rw_lock.v_read_count.dec()
					self.c_rw_lock.c_lock_read_count.release()
					return False
			self.c_rw_lock.c_lock_read_count.release()
			self.v_locked = True
			return True

		async def release(self) -> None:
			"""Release the lock."""
			if not self.v_locked: raise RELEASE_ERR_CLS(RELEASE_ERR_MSG)
			self.v_locked = False
			await self.c_rw_lock.c_lock_read_count.acquire()
			await self.c_rw_lock.v_read_count.dec()
			if 0 == int(self.c_rw_lock.v_read_count):
				self.c_rw_lock.c_resource.release()
			self.c_rw_lock.c_lock_read_count.release()

		def locked(self) -> bool:
			"""Answer to 'is it currently locked?'."""
			return self.v_locked

	class _aWriter(LockableD):
		def __init__(self, p_RWLock: "RWLockReadD") -> None:
			self.c_rw_lock = p_RWLock
			self.v_locked: bool = False
			super().__init__()

		async def acquire(self) -> bool:
			"""Acquire a lock."""
			locked: bool = await self.c_rw_lock.c_resource.acquire()
			self.v_locked = locked
			return locked

		async def downgrade(self) -> Lockable:
			"""Downgrade."""
			if not self.v_locked: raise RELEASE_ERR_CLS(RELEASE_ERR_MSG)

			result = self.c_rw_lock.gen_rlock()

			wait_blocking = asyncio.Event()

			async def lock_result() -> None:
				wait_blocking.set()
				await result.acquire()  # This is a blocking action
				wait_blocking.set()

			run_task(lock_result())

			await wait_blocking.wait()  # Wait for the thread to be almost in its blocking state.
			wait_blocking.clear() # TODO is this needed?

			await asyncio.sleep(sys.float_info.min * 123)  # Heuristic sleep delay to leave some extra time for the thread to block.

			await self.release()  # Open the gate! the current RW lock strategy gives priority to reader, therefore the result will acquire lock before any other writer lock.

			await wait_blocking.wait() # Wait for the lock to be acquired
			return result

		async def release(self) -> None:
			"""Release the lock."""
			if not self.v_locked: raise RELEASE_ERR_CLS(RELEASE_ERR_MSG)
			self.v_locked = False
			self.c_rw_lock.c_resource.release()

		def locked(self) -> bool:
			"""Answer to 'is it currently locked?'."""
			return self.v_locked

	def gen_rlock(self) -> "RWLockReadD._aReader":
		"""Generate a reader lock."""
		return RWLockReadD._aReader(self)

	def gen_wlock(self) -> "RWLockReadD._aWriter":
		"""Generate a writer lock."""
		return RWLockReadD._aWriter(self)

class RWLockWriteD(RWLockableD):
	"""A Read/Write lock giving preference to Writer."""

	def __init__(self, lock_factory: Callable[[], Lockable] = asyncio.Lock, time_source: Callable[[], float] = time.perf_counter) -> None:
		"""Init."""
		self.v_read_count: _ThreadSafeInt = _ThreadSafeInt(lock_factory=lock_factory, initial_value=0)
		self.v_write_count: int = 0
		self.c_time_source = time_source
		self.c_lock_read_count = lock_factory()
		self.c_lock_write_count = lock_factory()
		self.c_lock_read_entry = lock_factory()
		self.c_lock_read_try = lock_factory()
		self.c_resource = lock_factory()
		super().__init__()

	class _aReader(Lockable):
		def __init__(self, p_RWLock: "RWLockWriteD") -> None:
			self.c_rw_lock = p_RWLock
			self.v_locked: bool = False
			super().__init__()

		async def acquire(self) -> bool:
			"""Acquire a lock."""
			if not await self.c_rw_lock.c_lock_read_entry.acquire():
				return False
			if not await self.c_rw_lock.c_lock_read_try.acquire():
				self.c_rw_lock.c_lock_read_entry.release()
				return False
			if not await self.c_rw_lock.c_lock_read_count.acquire():
				self.c_rw_lock.c_lock_read_try.release()
				self.c_rw_lock.c_lock_read_entry.release()
				return False
			await self.c_rw_lock.v_read_count.inc()
			if 1 == int(self.c_rw_lock.v_read_count):
				if not await self.c_rw_lock.c_resource.acquire():
					self.c_rw_lock.c_lock_read_try.release()
					self.c_rw_lock.c_lock_read_entry.release()
					await self.c_rw_lock.v_read_count.dec()
					self.c_rw_lock.c_lock_read_count.release()
					return False
			self.c_rw_lock.c_lock_read_count.release()
			self.c_rw_lock.c_lock_read_try.release()
			self.c_rw_lock.c_lock_read_entry.release()
			self.v_locked = True
			return True

		async def release(self) -> None:
			"""Release the lock."""
			if not self.v_locked: raise RELEASE_ERR_CLS(RELEASE_ERR_MSG)
			self.v_locked = False
			await self.c_rw_lock.c_lock_read_count.acquire()
			await self.c_rw_lock.v_read_count.dec()
			if 0 == int(self.c_rw_lock.v_read_count):
				self.c_rw_lock.c_resource.release()
			self.c_rw_lock.c_lock_read_count.release()

		def locked(self) -> bool:
			"""Answer to 'is it currently locked?'."""
			return self.v_locked

	class _aWriter(LockableD):
		def __init__(self, p_RWLock: "RWLockWriteD") -> None:
			self.c_rw_lock = p_RWLock
			self.v_locked: bool = False
			super().__init__()

		async def acquire(self) -> bool:
			"""Acquire a lock."""
			if not await self.c_rw_lock.c_lock_write_count.acquire():
				return False
			self.c_rw_lock.v_write_count += 1
			if 1 == self.c_rw_lock.v_write_count:
				if not await self.c_rw_lock.c_lock_read_try.acquire():
					self.c_rw_lock.v_write_count -= 1
					self.c_rw_lock.c_lock_write_count.release()
					return False
			self.c_rw_lock.c_lock_write_count.release()
			if not await self.c_rw_lock.c_resource.acquire():
				await self.c_rw_lock.c_lock_write_count.acquire()
				self.c_rw_lock.v_write_count -= 1
				if 0 == self.c_rw_lock.v_write_count:
					self.c_rw_lock.c_lock_read_try.release()
				self.c_rw_lock.c_lock_write_count.release()
				return False
			self.v_locked = True
			return True

		async def downgrade(self) -> Lockable:
			"""Downgrade."""
			if not self.v_locked: raise RELEASE_ERR_CLS(RELEASE_ERR_MSG)
			await self.c_rw_lock.v_read_count.inc()

			self.v_locked = False
			await self.c_rw_lock.c_lock_write_count.acquire()
			self.c_rw_lock.v_write_count -= 1
			if 0 == self.c_rw_lock.v_write_count:
				self.c_rw_lock.c_lock_read_try.release()
			self.c_rw_lock.c_lock_write_count.release()

			result = self.c_rw_lock._aReader(p_RWLock=self.c_rw_lock)
			result.v_locked = True
			return result

		async def release(self) -> None:
			"""Release the lock."""
			if not self.v_locked: raise RELEASE_ERR_CLS(RELEASE_ERR_MSG)
			self.v_locked = False
			self.c_rw_lock.c_resource.release()
			await self.c_rw_lock.c_lock_write_count.acquire()
			self.c_rw_lock.v_write_count -= 1
			if 0 == self.c_rw_lock.v_write_count:
				self.c_rw_lock.c_lock_read_try.release()
			self.c_rw_lock.c_lock_write_count.release()

		def locked(self) -> bool:
			"""Answer to 'is it currently locked?'."""
			return self.v_locked

	def gen_rlock(self) -> "RWLockWriteD._aReader":
		"""Generate a reader lock."""
		return RWLockWriteD._aReader(self)

	def gen_wlock(self) -> "RWLockWriteD._aWriter":
		"""Generate a writer lock."""
		return RWLockWriteD._aWriter(self)

class RWLockFairD(RWLockableD):
	"""A Read/Write lock giving fairness to both Reader and Writer."""

	def __init__(self, lock_factory: Callable[[], Lockable] = asyncio.Lock, time_source: Callable[[], float] = time.perf_counter) -> None:
		"""Init."""
		self.v_read_count: int = 0
		self.c_time_source = time_source
		self.c_lock_read_count = lock_factory()
		self.c_lock_read = lock_factory()
		self.c_lock_write = lock_factory()
		super().__init__()

	class _aReader(Lockable):
		def __init__(self, p_RWLock: "RWLockFairD") -> None:
			self.c_rw_lock = p_RWLock
			self.v_locked: bool = False
			super().__init__()

		async def acquire(self) -> bool:
			"""Acquire a lock."""
			if not await self.c_rw_lock.c_lock_read.acquire():
				return False
			if not await self.c_rw_lock.c_lock_read_count.acquire():
				self.c_rw_lock.c_lock_read.release()
				return False
			self.c_rw_lock.v_read_count += 1
			if 1 == self.c_rw_lock.v_read_count:
				if not await self.c_rw_lock.c_lock_write.acquire():
					self.c_rw_lock.v_read_count -= 1
					self.c_rw_lock.c_lock_read_count.release()
					self.c_rw_lock.c_lock_read.release()
					return False
			self.c_rw_lock.c_lock_read_count.release()
			self.c_rw_lock.c_lock_read.release()
			self.v_locked = True
			return True

		async def release(self) -> None:
			"""Release the lock."""
			if not self.v_locked: raise RELEASE_ERR_CLS(RELEASE_ERR_MSG)
			self.v_locked = False
			await self.c_rw_lock.c_lock_read_count.acquire()
			self.c_rw_lock.v_read_count -= 1
			if 0 == self.c_rw_lock.v_read_count:
				self.c_rw_lock.c_lock_write.release()
			self.c_rw_lock.c_lock_read_count.release()

		def locked(self) -> bool:
			"""Answer to 'is it currently locked?'."""
			return self.v_locked

	class _aWriter(LockableD):
		def __init__(self, p_RWLock: "RWLockFairD") -> None:
			self.c_rw_lock = p_RWLock
			self.v_locked: bool = False
			super().__init__()

		async def acquire(self) -> bool:
			"""Acquire a lock."""
			if not await self.c_rw_lock.c_lock_read.acquire():
				return False
			if not await self.c_rw_lock.c_lock_write.acquire():
				self.c_rw_lock.c_lock_read.release()
				return False
			self.v_locked = True
			return True

		async def downgrade(self) -> Lockable:
			"""Downgrade."""
			if not self.v_locked: raise RELEASE_ERR_CLS(RELEASE_ERR_MSG)
			self.c_rw_lock.v_read_count += 1

			self.v_locked = False
			self.c_rw_lock.c_lock_read.release()

			result = self.c_rw_lock._aReader(p_RWLock=self.c_rw_lock)
			result.v_locked = True
			return result

		async def release(self) -> None:
			"""Release the lock."""
			if not self.v_locked: raise RELEASE_ERR_CLS(RELEASE_ERR_MSG)
			self.v_locked = False
			self.c_rw_lock.c_lock_write.release()
			self.c_rw_lock.c_lock_read.release()

		def locked(self) -> bool:
			"""Answer to 'is it currently locked?'."""
			return self.v_locked

	def gen_rlock(self) -> "RWLockFairD._aReader":
		"""Generate a reader lock."""
		return RWLockFairD._aReader(self)

	def gen_wlock(self) -> "RWLockFairD._aWriter":
		"""Generate a writer lock."""
		return RWLockFairD._aWriter(self)
