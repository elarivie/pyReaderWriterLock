#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Unit tests."""

import unittest
import sys
import time
import asyncio

from typing import List
from typing import Union

from readerwriterlock import rwlock_async as rwlock


class TestRWLock_Async(unittest.TestCase):
	"""Test RWLock different strategies."""

	def setUp(self) -> None:
		"""Test setup."""
		self.c_rwlock_type_downgradable = (rwlock.RWLockReadD, rwlock.RWLockWriteD, rwlock.RWLockFairD)
		self.c_rwlock_type = (rwlock.RWLockRead, rwlock.RWLockWrite, rwlock.RWLockFair) + self.c_rwlock_type_downgradable

	def test_multi_async(self) -> None:
		"""
		# Given: Bunch of reader & writer lock generated from a RW lock.

		# When: Locking/unlocking in a multi thread setup.

		# Then: the locks shall not deadlock.
		"""
		s_period_sec: int = 60
		print(f"test_MultiThread {s_period_sec * len(self.c_rwlock_type)} sec…", flush=True)
		exception_occured: bool = False
		async def run_tests():
			for c_curr_lock_type in self.c_rwlock_type:
				with self.subTest(c_curr_lock_type):
					print(f"    {c_curr_lock_type} …", end="", flush=True)
					c_curr_rw_lock: Union[rwlock.RWLockable, rwlock.RWLockableD] = c_curr_lock_type()
					v_value: int = 0

					async def downgrader1() -> None:
						"""Downgrader using a blocking acquire strategy."""
						if c_curr_lock_type not in self.c_rwlock_type_downgradable: return
						try:
							nonlocal v_value
							c_enter_time = time.time()
							while time.time() - c_enter_time <= s_period_sec:
								c_lock_w1: Union[rwlock.Lockable, rwlock.LockableD] = c_curr_rw_lock.gen_wlock()
								assert isinstance(c_lock_w1, rwlock.LockableD), type(c_lock_w1)

								await asyncio.sleep(sys.float_info.min)

								locked: bool = await c_lock_w1.acquire()
								if locked:
									try:
										# Assert like a writer
										v_temp = v_value
										v_value += 1
										self.assertEqual(v_value, (v_temp + 1))

										assert isinstance(c_lock_w1, rwlock.LockableD), c_lock_w1
										c_lock_w1 = await c_lock_w1.downgrade()
										assert isinstance(c_lock_w1, rwlock.Lockable), c_lock_w1
										# Assert like a reader
										vv_value: int = v_value
										await asyncio.sleep(sys.float_info.min)
										self.assertEqual(vv_value, v_value)

										await asyncio.sleep(sys.float_info.min)
									finally:
										await c_lock_w1.release()
						except BaseException:  # pragma: no cover
							nonlocal exception_occured
							exception_occured = True
							raise

					async def writer1() -> None:
						"""Writer using a blocking acquire strategy."""
						try:
							nonlocal v_value
							c_enter_time = time.time()
							c_lock_w1 = c_curr_rw_lock.gen_wlock()
							while time.time() - c_enter_time <= s_period_sec:
								await asyncio.sleep(sys.float_info.min)
								async with c_lock_w1:
									v_temp = v_value
									v_value += 1
									self.assertEqual(v_value, v_temp + 1)
									await asyncio.sleep(sys.float_info.min)
						except BaseException:  # pragma: no cover
							nonlocal exception_occured
							exception_occured = True
							raise

					async def writer2() -> None:
						"""Writer using a timeout blocking acquire strategy."""
						try:
							nonlocal v_value
							c_enter_time = time.time()
							c_lock_w1 = c_curr_rw_lock.gen_wlock()
							while time.time() - c_enter_time <= s_period_sec:
								await asyncio.sleep(sys.float_info.min)
								locked: bool
								try:
									locked = await c_lock_w1.acquire(blocking=True, timeout=sys.float_info.min)
									if locked:
										v_temp = v_value
										v_value += 1
										self.assertEqual(v_value, (v_temp + 1))
										await asyncio.sleep(sys.float_info.min)
								finally:
									if locked:
										await c_lock_w1.release()
						except BaseException:  # pragma: no cover
							nonlocal exception_occured
							exception_occured = True
							raise

					async def reader1() -> None:
								"""Reader using a no timeout blocking acquire strategy."""
								try:
									nonlocal v_value
									c_enter_time = time.time()
									c_lock_r1 = c_curr_rw_lock.gen_rlock()
									while time.time() - c_enter_time <= s_period_sec:
										await asyncio.sleep(sys.float_info.min)
										async with c_lock_r1:
											vv_value: int = v_value
											await asyncio.sleep(sys.float_info.min)
											self.assertEqual(vv_value, v_value)
								except BaseException:  # pragma: no cover
									nonlocal exception_occured
									exception_occured = True
									raise

					async def reader2() -> None:
						"""Reader using a timeout blocking acquire strategy."""
						try:
							nonlocal v_value
							c_enter_time = time.time()
							c_lock_r2 = c_curr_rw_lock.gen_rlock()
							while time.time() - c_enter_time <= s_period_sec:
								await asyncio.sleep(sys.float_info.min)
								locked: bool = False
								try:
									locked = await c_lock_r2.acquire(blocking=True, timeout=sys.float_info.min)
									if locked:
										vv_value: int = v_value
										await asyncio.sleep(sys.float_info.min)
										self.assertEqual(vv_value, v_value)
								finally:
									if locked:
										await c_lock_r2.release()
						except BaseException:  # pragma: no cover
							nonlocal exception_occured
							exception_occured = True
							raise

					tasks = []
					for _ in range(50):
						tasks.extend([writer1(),writer2(),reader1(),reader2(),downgrader1()])
					await asyncio.gather(*tasks)

					self.assertGreater(v_value, 0)
					self.assertFalse(exception_occured)
					print("\x1b[1;32m✓\x1b[0m", flush=True)


		eloop = asyncio.get_event_loop()
		eloop.run_until_complete(run_tests())
		self.assertEqual(len(asyncio.all_tasks(eloop)), 0)

class TestRWLockSpecificCase(unittest.TestCase):
	"""Test RW Locks in specific requirements."""

	def setUp(self) -> None:
		"""Test setup."""
		self.c_rwlock_type_downgradable = (rwlock.RWLockWriteD, rwlock.RWLockFairD, rwlock.RWLockReadD)
		self.c_rwlock_type = (rwlock.RWLockRead, rwlock.RWLockWrite, rwlock.RWLockFair) + self.c_rwlock_type_downgradable

	def test_write_req00(self) -> None:
		"""
		# Given: a RW lock type.

		# When: requesting a new instance without parameters.

		# Then: a new RW lock is provided.
		"""
		# ## Arrange
		for current_rw_lock_type in self.c_rwlock_type:
			with self.subTest(current_rw_lock_type):
				# ## Act
				result = current_rw_lock_type()
				# ## Assert
				self.assertIsInstance(result, current_rw_lock_type)

	def test_write_req01(self) -> None:
		"""
		# Given: a RW lock type.

		# When: requesting a new instance with all possible parameters.

		# Then: a new RW lock is provided.
		"""
		# ## Arrange
		for current_rw_lock_type in self.c_rwlock_type:
			with self.subTest(current_rw_lock_type):
				# ## Act
				result = current_rw_lock_type(lock_factory=asyncio.Lock, time_source=time.perf_counter)
				# ## Assert
				self.assertIsInstance(result, current_rw_lock_type)

	def test_write_req02(self) -> None:
		"""
		# Given: a RW lock type to instantiate a RW lock.

		# When: generating reader lock using the instance.

		# Then: an unlocked reader lock is provided.
		"""
		# ## Arrange
		for current_rw_lock_type in self.c_rwlock_type:
			with self.subTest(current_rw_lock_type):
				# ## Act
				result = current_rw_lock_type().gen_rlock()
				# ## Assert
				self.assertIsInstance(result, rwlock.Lockable)
				self.assertFalse(result.locked())

	def test_write_req03(self) -> None:
		"""
		# Given: a RW lock type to instantiate a RW lock.

		# When: generating writer lock using the instance.

		# Then: an unlocked writer lock is provided.
		"""
		# ## Arrange
		for current_rw_lock_type in self.c_rwlock_type:
			with self.subTest(current_rw_lock_type):
				# ## Act
				result = current_rw_lock_type().gen_wlock()
				# ## Assert
				self.assertIsInstance(result, rwlock.Lockable)
				self.assertFalse(result.locked())

	def test_write_req04(self) -> None:
		"""
		# Given: a RW lock type to instantiate a RW lock.

		# When: generating reader/writer lock using the instance.

		# Then: the generated locks support context manager.
		"""
		# ## Arrange
		eloop = asyncio.get_event_loop()
		for current_rw_lock_type in self.c_rwlock_type:
			with self.subTest(current_rw_lock_type):
				for current_lock in (current_rw_lock_type().gen_rlock(), current_rw_lock_type().gen_wlock()):
					with self.subTest(current_lock):
						# ## Act
						async def try_lock():
							async with current_lock:
								# ## Assert
								self.assertTrue(current_lock.locked())
							self.assertFalse(current_lock.locked())
						eloop.run_until_complete(try_lock())

	def test_write_req05(self) -> None:
		"""
		# Given: a RW lock type to instantiate a RW lock.

		# When: generating reader/writer lock using the instance.

		# Then: the generated locks raise an exception if released while being unlocked.
		"""
		# ## Arrange
		try:
			asyncio.Lock().release()
		except RuntimeError as exc:
			eloop = asyncio.get_event_loop()
			for current_rw_lock_type in self.c_rwlock_type:
				with self.subTest(current_rw_lock_type):
					for current_lock in (current_rw_lock_type().gen_rlock(), current_rw_lock_type().gen_wlock()):
						with self.subTest(current_lock):
							# ## Act
							async def try_lock():
								with self.assertRaises(exc.__class__) as err:
									await current_lock.release()
								self.assertEqual(str(err.exception), str(exc))
							eloop.run_until_complete(try_lock())

	def test_write_req06(self) -> None:
		"""
		# Given: a RW lock type to instantiate a RW lock.

		# When: generating reader/writer lock using the instance and a writer successfully acquire its lock.

		# Then: No other writer can successfully acquire a lock in a non blocking way.
		"""
		# ## Arrange
		eloop = asyncio.get_event_loop()
		for current_rw_lock_type in self.c_rwlock_type:
			with self.subTest(current_rw_lock_type):
				async def try_lock():
					current_lock = current_rw_lock_type()
					async with current_lock.gen_wlock():
						# ## Act
						result = await current_lock.gen_wlock().acquire(blocking=False)
						# ## Assert
						self.assertFalse(result)
				eloop.run_until_complete(try_lock())

	def test_write_req07(self) -> None:
		"""
		# Given: a RW lock type to instantiate a RW lock.

		# When: generating reader/writer lock using the instance and a writer successfully acquire its lock.

		# Then: No reader can successfully acquire a lock in a non blocking way.
		"""
		# ## Arrange
		eloop = asyncio.get_event_loop()
		for current_rw_lock_type in self.c_rwlock_type:
			with self.subTest(current_rw_lock_type):
				async def try_lock():
					current_lock = current_rw_lock_type()
					async with current_lock.gen_wlock():
						# ## Act
						result = await current_lock.gen_rlock().acquire(blocking=False)
						# ## Assert
						self.assertFalse(result)
				eloop.run_until_complete(try_lock())
				

	def test_write_req08(self) -> None:
		"""
		# Given: a RW lock type to instantiate a RW lock.

		# When: generating reader/writer lock using the instance and a writer successfully acquire its lock.

		# Then: No other writer can successfully acquire a lock in a blocking way.
		"""
		# ## Arrange
		eloop = asyncio.get_event_loop()
		for current_rw_lock_type in self.c_rwlock_type:
			with self.subTest(current_rw_lock_type):
				async def try_lock():
					current_lock = current_rw_lock_type()
					async with current_lock.gen_wlock():
						# ## Act
						result = await current_lock.gen_wlock().acquire(blocking=True, timeout=0.75)
						# ## Assert
						self.assertFalse(result)
				eloop.run_until_complete(try_lock())

	def test_write_req09(self) -> None:
		"""
		# Given: a RW lock type to instantiate a RW lock.

		# When: generating reader/writer lock using the instance and a writer successfully acquire its lock.

		# Then: No reader can successfully acquire a lock in a blocking way.
		"""
		# ## Arrange
		eloop = asyncio.get_event_loop()
		for current_rw_lock_type in self.c_rwlock_type:
			with self.subTest(current_rw_lock_type):
				async def try_lock():
					current_lock = current_rw_lock_type()
					async with current_lock.gen_wlock():
						# ## Act
						result = await current_lock.gen_rlock().acquire(blocking=True, timeout=0.75)
						# ## Assert
						self.assertFalse(result)
				eloop.run_until_complete(try_lock())

	def test_write_req10(self) -> None:
		"""
		# Given: a RW lock type to instantiate a RW lock.

		# When: generating reader/writer lock using the instance and a reader successfully acquire its lock.

		# Then: No other writer can successfully acquire a lock in a non blocking way.
		"""
		# ## Arrange
		eloop = asyncio.get_event_loop()
		for current_rw_lock_type in self.c_rwlock_type:
			with self.subTest(current_rw_lock_type):
				async def try_lock():
					current_lock = current_rw_lock_type()
					async with current_lock.gen_rlock():
						# ## Act
						result = await current_lock.gen_wlock().acquire(blocking=False)
						# ## Assert
						self.assertFalse(result)
				eloop.run_until_complete(try_lock())

	def test_write_req11(self) -> None:
		"""
		# Given: a RW lock type to instantiate a RW lock.

		# When: generating reader/writer lock using the instance and a reader successfully acquire its lock.

		# Then: No other writer can successfully acquire a lock in a blocking way.
		"""
		# ## Arrange
		eloop = asyncio.get_event_loop()
		for current_rw_lock_type in self.c_rwlock_type:
			with self.subTest(current_rw_lock_type):
				async def try_lock():
					current_lock = current_rw_lock_type()
					async with current_lock.gen_rlock():
						# ## Act
						result = await current_lock.gen_wlock().acquire(blocking=True, timeout=0.75)
						# ## Assert
						self.assertFalse(result)
				eloop.run_until_complete(try_lock())

	def test_write_req12(self) -> None:
		"""
		# Given: a RW lock type to instantiate a RW lock.

		# When: generating reader/writer lock using the instance and a reader successfully acquire its lock.

		# Then: other reader can also successfully acquire a lock in a non-blocking way.
		"""
		# ## Arrange
		eloop = asyncio.get_event_loop()
		for current_rw_lock_type in self.c_rwlock_type:
			with self.subTest(current_rw_lock_type):
				async def try_lock():
					current_lock = current_rw_lock_type()
					async with current_lock.gen_rlock():
						other_lock = current_lock.gen_rlock()
						# ## Act
						result = await other_lock.acquire(blocking=False)
						# ## Assert
						self.assertTrue(result)
				eloop.run_until_complete(try_lock())

	def test_write_req13(self) -> None:
		"""
		# Given: a RW lock type to instantiate a RW lock.

		# When: generating reader/writer lock using the instance and a reader successfully acquire its lock.

		# Then: other reader can also successfully acquire a lock in a blocking way.
		"""
		# ## Arrange
		eloop = asyncio.get_event_loop()
		for current_rw_lock_type in self.c_rwlock_type:
			with self.subTest(current_rw_lock_type):
				async def try_lock():
					current_lock = current_rw_lock_type()
					async with current_lock.gen_rlock():
						# ## Act
						other_lock = current_lock.gen_rlock()
						try:
							result = await other_lock.acquire(blocking=True, timeout=0.75)
							# ## Assert
							self.assertTrue(result)
							# ## Clean
						finally:
							await other_lock.release()
				eloop.run_until_complete(try_lock())

	def test_write_req14(self) -> None:
		"""
		# Given: a Downgradable RW lock type to instantiate a RW lock.

		# When: A a generated writer lock successfully acquire its lock.

		# Then: It is possible to downgrade Locked Write to Locked Read.
		"""
		# ## Arrange
		eloop = asyncio.get_event_loop()
		for current_rw_lock_type in self.c_rwlock_type_downgradable:
			with self.subTest(current_rw_lock_type):
				async def try_lock():
					current_rw_lock = current_rw_lock_type()
					assert isinstance(current_rw_lock, rwlock.RWLockableD)
					current_lock: Union[rwlock.LockableD, rwlock.Lockable] = current_rw_lock.gen_wlock()
					other_lock = current_rw_lock.gen_rlock()

					self.assertFalse(current_lock.locked())
					self.assertTrue(await current_lock.acquire())
					self.assertTrue(current_lock.locked())
					self.assertFalse(other_lock.locked())
					try:
						# ## Act
						self.assertFalse(await other_lock.acquire(blocking=False))
						assert isinstance(current_lock, rwlock.LockableD)
						current_lock = await current_lock.downgrade()
						self.assertTrue(await other_lock.acquire())
						self.assertTrue(other_lock.locked())

					finally:
						await current_lock.release()
					try:
						result = await other_lock.acquire(blocking=True, timeout=0.75)
						# ## Assert
						self.assertTrue(result)
						# ## Clean
					finally:
						await other_lock.release()
				eloop.run_until_complete(try_lock())

	def test_write_req15(self) -> None:
		"""
		# Given: a Downgradable RW lock type to instantiate a RW lock.

		# When: A a generated writer lock is downgrade but it wasn't in a locked state.

		# Then: the generated locks raise an exception if released while being unlocked.
		"""
		# ## Arrange
		eloop = asyncio.get_event_loop()
		for current_rw_lock_type in self.c_rwlock_type_downgradable:
			with self.subTest(current_rw_lock_type):
				async def try_lock():
					current_rw_lock = current_rw_lock_type()
					assert isinstance(current_rw_lock, rwlock.RWLockableD)
					current_lock: Union[rwlock.LockableD] = current_rw_lock.gen_wlock()

					with self.assertRaises(rwlock.RELEASE_ERR_CLS) as err:
						await current_lock.release()
					self.assertEqual(str(err.exception), str(rwlock.RELEASE_ERR_MSG))

					with self.assertRaises(rwlock.RELEASE_ERR_CLS):
						# ## Assume
						self.assertFalse((current_lock.locked()))
						# ## Act
						await current_lock.downgrade()

					self.assertFalse(current_lock.locked())
				eloop.run_until_complete(try_lock())

class TestWhiteBoxRWLockReadD(unittest.TestCase):
	"""Test RWLockReadD internal specifity."""

	def test_read_vs_downgrade_read(self) -> None:
		"""
		# Given: Instance of RWLockReadD.

		# When: A reader lock is acquired OR A writer lock is downgraded.

		# Then: The internal state should be the same.
		"""
		# ## Arrange
		c_rwlock_1 = rwlock.RWLockReadD()
		c_rwlock_2 = rwlock.RWLockReadD()
		eloop = asyncio.get_event_loop()

		def assert_internal_state():
			self.assertEqual(int(c_rwlock_1.v_read_count), int(c_rwlock_2.v_read_count))
			self.assertEqual(bool(c_rwlock_1.c_resource.locked()), bool(c_rwlock_2.c_resource.locked()))
			self.assertEqual(bool(c_rwlock_1.c_lock_read_count.locked()), bool(c_rwlock_2.c_lock_read_count.locked()))
		# ## Assume
		assert_internal_state()

		# ## Act
		async def try_lock():
			a_read_lock = c_rwlock_1.gen_rlock()
			await a_read_lock.acquire()
			a_downgrade_lock: Union[rwlock.Lockable, rwlock.LockableD] = c_rwlock_2.gen_wlock()
			await a_downgrade_lock.acquire()
			self.assertIsInstance(a_downgrade_lock, rwlock.LockableD)
			a_downgrade_lock = await a_downgrade_lock.downgrade()
			# ## Assert
			assert_internal_state()

			await a_read_lock.release()
			await a_downgrade_lock.release()
			assert_internal_state()
		eloop.run_until_complete(try_lock())

	def test_read_vs_downgrade_write(self) -> None:
		"""
		# Given: Instance of RWLockWriteD.

		# When: A reader lock is acquired OR A writer lock is downgraded.

		# Then: The internal state should be the same.
		"""
		# ## Arrange
		c_rwlock_1 = rwlock.RWLockWriteD()
		c_rwlock_2 = rwlock.RWLockWriteD()
		eloop = asyncio.get_event_loop()

		def assert_internal_state():
			self.assertEqual(int(c_rwlock_1.v_read_count), int(c_rwlock_2.v_read_count))
			self.assertEqual(int(c_rwlock_1.v_write_count), int(c_rwlock_2.v_write_count))
			self.assertEqual(bool(c_rwlock_1.c_lock_read_count.locked()), bool(c_rwlock_2.c_lock_read_count.locked()))
			self.assertEqual(bool(c_rwlock_1.c_lock_write_count.locked()), bool(c_rwlock_2.c_lock_write_count.locked()))

			self.assertEqual(bool(c_rwlock_1.c_lock_read_entry.locked()), bool(c_rwlock_2.c_lock_read_entry.locked()))
			self.assertEqual(bool(c_rwlock_1.c_lock_read_try.locked()), bool(c_rwlock_2.c_lock_read_try.locked()))
			self.assertEqual(bool(c_rwlock_1.c_resource.locked()), bool(c_rwlock_2.c_resource.locked()))

		# ## Assume
		assert_internal_state()

		# ## Act
		async def try_lock():
			a_read_lock = c_rwlock_1.gen_rlock()
			await a_read_lock.acquire()
			a_downgrade_lock: Union[rwlock.LockableD, rwlock.Lockable] = c_rwlock_2.gen_wlock()
			await a_downgrade_lock.acquire()
			self.assertIsInstance(a_downgrade_lock, rwlock.LockableD)
			a_downgrade_lock = await a_downgrade_lock.downgrade()
			# ## Assert
			assert_internal_state()

			await a_read_lock.release()
			await a_downgrade_lock.release()
			assert_internal_state()
		eloop.run_until_complete(try_lock())

	def test_read_vs_downgrade_fair(self) -> None:
		"""
		# Given: Instance of RWLockFairD.

		# When: A reader lock is acquired OR A writer lock is downgraded.

		# Then: The internal state should be the same.
		"""
		# ## Arrange
		c_rwlock_1 = rwlock.RWLockFairD()
		c_rwlock_2 = rwlock.RWLockFairD()
		eloop = asyncio.get_event_loop()

		def assert_internal_state():
			"""Assert internal."""
			self.assertEqual(int(c_rwlock_1.v_read_count), int(c_rwlock_2.v_read_count))
			self.assertEqual(bool(c_rwlock_1.c_lock_read_count.locked()), bool(c_rwlock_2.c_lock_read_count.locked()))
			self.assertEqual(bool(c_rwlock_1.c_lock_read.locked()), bool(c_rwlock_2.c_lock_read.locked()))
			self.assertEqual(bool(c_rwlock_1.c_lock_write.locked()), bool(c_rwlock_2.c_lock_write.locked()))

		# ## Assume
		assert_internal_state()

		# ## Act
		async def try_lock():
			a_read_lock = c_rwlock_1.gen_rlock()
			await a_read_lock.acquire()
			a_downgrade_lock: Union[rwlock.LockableD, rwlock.Lockable] = c_rwlock_2.gen_wlock()
			await a_downgrade_lock.acquire()
			assert isinstance(a_downgrade_lock, rwlock.LockableD)
			a_downgrade_lock = await a_downgrade_lock.downgrade()
			# ## Assert
			assert_internal_state()

			await a_read_lock.release()
			await a_downgrade_lock.release()
			assert_internal_state()
		eloop.run_until_complete(try_lock())


if "__main__" == __name__:
	unittest.main(failfast=False)  # pragma: no cover
