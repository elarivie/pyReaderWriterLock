#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Unit tests."""

import unittest


class TestRWLock(unittest.TestCase):
	"""Test RWLock different strategies."""

	def setUp(self):
		"""Test setup."""
		self.v_value = 0
		from readerwriterlock import rwlock
		self.c_rwlock_instance = [rwlock.RWLockRead(), rwlock.RWLockWrite(), rwlock.RWLockFair()]

	def test_single_access(self):
		"""Test single access."""
		print("test_SingleAccess")
		for c_curr_lock in self.c_rwlock_instance:
			with self.subTest(c_curr_lock):
				for c_curr_lock_x in [c_curr_lock.gen_rlock(), c_curr_lock.gen_wlock()]:
					self.assertFalse(c_curr_lock_x.locked())
					with c_curr_lock_x:
						self.assertTrue(c_curr_lock_x.locked())
					self.assertFalse(c_curr_lock_x.locked())
					for c_params in [[0, -1], [1, -1], [1, 0], [1, 1]]:
						with self.subTest([c_curr_lock, c_curr_lock_x, c_params]):
							self.assertTrue(c_curr_lock_x.acquire(blocking=c_params[0], timeout=c_params[1]))
							self.assertTrue(c_curr_lock_x.locked())
							c_curr_lock_x.release()
							self.assertFalse(c_curr_lock_x.locked())
							with self.assertRaises(RuntimeError):
								c_curr_lock_x.release()

	def test_multi_read(self):
		"""Test multi read."""
		print("test_MultiRead")
		for c_curr_lock in self.c_rwlock_instance:
			with self.subTest(c_curr_lock):
				c_lock_r0 = c_curr_lock.gen_rlock()
				c_lock_r1 = c_curr_lock.gen_rlock()
				c_lock_w1 = c_curr_lock.gen_wlock()

				self.assertTrue(c_lock_r0.acquire())
				self.assertTrue(c_lock_r1.acquire())
				self.assertTrue(c_lock_r0.locked())
				self.assertTrue(c_lock_r1.locked())
				self.assertFalse(c_lock_w1.acquire(blocking=True, timeout=1))
				self.assertFalse(c_lock_w1.locked())
				c_lock_r1.release()
				self.assertTrue(c_lock_r0.locked())
				self.assertFalse(c_lock_r1.locked())
				self.assertFalse(c_lock_w1.acquire(blocking=True, timeout=1))
				self.assertFalse(c_lock_w1.locked())
				c_lock_r0.release()
				self.assertFalse(c_lock_r0.locked())
				self.assertFalse(c_lock_r1.locked())
				self.assertTrue(c_lock_w1.acquire(blocking=True, timeout=1))
				self.assertTrue(c_lock_w1.locked())
				self.assertFalse(c_lock_r0.acquire(blocking=True, timeout=1))
				self.assertFalse(c_lock_r0.locked())
				c_lock_w1.release()
				self.assertFalse(c_lock_w1.locked())

	def test_multi_write(self):
		"""Test multi write."""
		print("test_MultiWrite")
		for c_curr_lock in self.c_rwlock_instance:
			with self.subTest(c_curr_lock):
				c_lock_r0 = c_curr_lock.gen_rlock()
				c_lock_r1 = c_curr_lock.gen_rlock()
				c_lock_w0 = c_curr_lock.gen_wlock()
				c_lock_w1 = c_curr_lock.gen_wlock()
				self.assertTrue(c_lock_w0.acquire())
				self.assertTrue(c_lock_w0.locked())
				self.assertFalse(c_lock_w1.acquire(blocking=False))
				self.assertFalse(c_lock_w1.locked())
				self.assertFalse(c_lock_w1.acquire(blocking=True, timeout=1))
				self.assertFalse(c_lock_w1.locked())
				c_lock_w0.release()

				self.assertTrue(c_lock_r0.acquire())
				self.assertTrue(c_lock_r0.locked())
				self.assertFalse(c_lock_w1.acquire(blocking=False))
				self.assertFalse(c_lock_w1.locked())
				self.assertFalse(c_lock_w1.acquire(blocking=True, timeout=1))
				self.assertFalse(c_lock_w1.locked())
				self.assertTrue(c_lock_r1.acquire())
				self.assertTrue(c_lock_r1.locked())
				c_lock_r0.release()
				c_lock_r1.release()
				self.assertFalse(c_lock_r0.locked())
				self.assertFalse(c_lock_r1.locked())

	def test_multi_thread(self):
		"""Test Multi Thread."""
		import threading
		import time
		s_period_sec = 60
		print("test_MultiThread (" + str(s_period_sec * len(self.c_rwlock_instance)) + " sec)")
		c_value_end = []
		for c_curr_lock in self.c_rwlock_instance:
			def writer1():
				"""Writer."""
				c_enter_time = time.time()
				c_lock_w1 = c_curr_lock.gen_wlock()
				while time.time() - c_enter_time <= s_period_sec:
					time.sleep(0)
					c_lock_w1.acquire()
					v_temp = self.v_value
					self.v_value += 1
					assert self.v_value == (v_temp + 1)
					time.sleep(0.1)
					c_lock_w1.release()

			def reader1():
				"""Reader."""
				c_enter_time = time.time()
				c_lock_r1 = c_curr_lock.gen_rlock()
				while time.time() - c_enter_time <= s_period_sec:
					time.sleep(0)
					with c_lock_r1:
						vv_value = self.v_value
						time.sleep(2)
						assert vv_value == self.v_value

			with self.subTest(c_curr_lock):
				threadsarray = []
				for i in range(10):
					threadsarray.append(threading.Thread(group=None, target=writer1, name="writer" + str(i), daemon=False))
					threadsarray.append(threading.Thread(group=None, target=reader1, name="reader" + str(i), daemon=False))
				for c_curr_thread in threadsarray:
					c_curr_thread.start()
				for c_curr_thread in threadsarray:
					while c_curr_thread.is_alive():
						time.sleep(0.5)
				c_value_end.append(self.v_value)
		with self.subTest(c_value_end):
			self.assertEqual(len(c_value_end), 3)
			self.assertGreater(c_value_end[0], 0)
			self.assertGreater(c_value_end[1], c_value_end[0])
			self.assertGreater(c_value_end[2], c_value_end[1])
			c_priority_r = c_value_end[0] - 0
			c_priority_w = c_value_end[1] - c_value_end[0]
			c_priority_f = c_value_end[2] - c_value_end[1]
			self.assertGreater(c_priority_w, c_priority_r)
			self.assertGreater(c_priority_w, c_priority_f)
			self.assertGreater(c_priority_f, c_priority_r)


if __name__ == '__main__':
	unittest.main(failfast=False)
