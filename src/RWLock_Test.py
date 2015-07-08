#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

class TestStringMethods(unittest.TestCase):

	def setUp(self):
		self.V_Value = 0
		import RWLock
		self.C_RWLockInstance = [RWLock.RWLockRead(), RWLock.RWLockWrite(), RWLock.RWLockFair()]

	def test_SingleAccess(self):
		print("test_SingleAccess")
		for c_CurrLock in self.C_RWLockInstance:
			with self.subTest(c_CurrLock):
				for c_CurrLockX in [c_CurrLock.genRlock(), c_CurrLock.genWlock()]:
					self.assertFalse(c_CurrLockX.locked())
					with c_CurrLockX:
						self.assertTrue(c_CurrLockX.locked())
					self.assertFalse(c_CurrLockX.locked())
					for c_Params in [[0, -1], [1, -1], [1, 0], [1, 1]]:
						with self.subTest([c_CurrLock, c_CurrLockX, c_Params]):
							self.assertTrue(c_CurrLockX.acquire(blocking=c_Params[0], timeout=c_Params[1]))
							self.assertTrue(c_CurrLockX.locked())
							c_CurrLockX.release()
							self.assertFalse(c_CurrLockX.locked())
							with self.assertRaises(RuntimeError):
								c_CurrLockX.release()

	def test_MultiRead(self):
		print("test_MultiRead")
		for c_CurrLock in self.C_RWLockInstance:
			with self.subTest(c_CurrLock):
				c_LockR0 = c_CurrLock.genRlock()
				c_LockR1 = c_CurrLock.genRlock()
				c_LockW1 = c_CurrLock.genWlock()

				self.assertTrue(c_LockR0.acquire())
				self.assertTrue(c_LockR1.acquire())
				self.assertTrue(c_LockR0.locked())
				self.assertTrue(c_LockR1.locked())
				self.assertFalse(c_LockW1.acquire(blocking=True, timeout=1))
				self.assertFalse(c_LockW1.locked())
				c_LockR1.release()
				self.assertTrue(c_LockR0.locked())
				self.assertFalse(c_LockR1.locked())
				self.assertFalse(c_LockW1.acquire(blocking=True, timeout=1))
				self.assertFalse(c_LockW1.locked())
				c_LockR0.release()
				self.assertFalse(c_LockR0.locked())
				self.assertFalse(c_LockR1.locked())
				self.assertTrue(c_LockW1.acquire(blocking=True, timeout=1))
				self.assertTrue(c_LockW1.locked())
				self.assertFalse(c_LockR0.acquire(blocking=True, timeout=1))
				self.assertFalse(c_LockR0.locked())
				c_LockW1.release()
				self.assertFalse(c_LockW1.locked())

	def test_MultiWrite(self):
		print("test_MultiWrite")
		for c_CurrLock in self.C_RWLockInstance:
			with self.subTest(c_CurrLock):
				c_LockR0 = c_CurrLock.genRlock()
				c_LockR1 = c_CurrLock.genRlock()
				c_LockW0 = c_CurrLock.genWlock()
				c_LockW1 = c_CurrLock.genWlock()
				self.assertTrue(c_LockW0.acquire())
				self.assertTrue(c_LockW0.locked())
				self.assertFalse(c_LockW1.acquire(blocking=False))
				self.assertFalse(c_LockW1.locked())
				self.assertFalse(c_LockW1.acquire(blocking=True, timeout=1))
				self.assertFalse(c_LockW1.locked())
				c_LockW0.release()

				self.assertTrue(c_LockR0.acquire())
				self.assertTrue(c_LockR0.locked())
				self.assertFalse(c_LockW1.acquire(blocking=False))
				self.assertFalse(c_LockW1.locked())
				self.assertFalse(c_LockW1.acquire(blocking=True, timeout=1))
				self.assertFalse(c_LockW1.locked())
				self.assertTrue(c_LockR1.acquire())
				self.assertTrue(c_LockR1.locked())
				c_LockR0.release()
				c_LockR1.release()
				self.assertFalse(c_LockR0.locked())
				self.assertFalse(c_LockR1.locked())

	def test_MultiThread(self):
		s_PeriodSec = 60
		print("test_MultiThread (" + str(s_PeriodSec * len(self.C_RWLockInstance)) + " sec)")
		def writer1():
			c_EnterTime = time.time()
			c_Lockw1 = c_CurrLock.genWlock()
			while time.time() - c_EnterTime <= s_PeriodSec:
				time.sleep(0)
				c_Lockw1.acquire()
				v_Temp = self.V_Value
				self.V_Value += 1
				assert self.V_Value == (v_Temp + 1)
				time.sleep(0.1)
				c_Lockw1.release()
		def reader1():
			c_EnterTime = time.time()
			c_Lockr1 = c_CurrLock.genRlock()
			while time.time() - c_EnterTime <= s_PeriodSec:
				time.sleep(0)
				with c_Lockr1:
					vv_Value = self.V_Value
					time.sleep(2)
					assert vv_Value == self.V_Value
		import threading
		import time
		c_ValueEnd = []
		for c_CurrLock in self.C_RWLockInstance:
			with self.subTest(c_CurrLock):
				threadsarray = []
				for i in range(10):
					threadsarray.append(threading.Thread(group=None, target=writer1, name="writer" + str(i), daemon=False))
					threadsarray.append(threading.Thread(group=None, target=reader1, name="reader" + str(i), daemon=False))
				for c_CurrThread in threadsarray:
					c_CurrThread.start()
				for c_CurrThread in threadsarray:
					while c_CurrThread.is_alive():
						time.sleep(0.5)
				c_ValueEnd.append(self.V_Value)
		with self.subTest(c_ValueEnd):
			self.assertEqual(len(c_ValueEnd), 3)
			self.assertGreater(c_ValueEnd[0], 0)
			self.assertGreater(c_ValueEnd[1], c_ValueEnd[0])
			self.assertGreater(c_ValueEnd[2], c_ValueEnd[1])
			c_PriorityR = c_ValueEnd[0] - 0
			c_PriorityW = c_ValueEnd[1] - c_ValueEnd[0]
			c_PriorityF = c_ValueEnd[2] - c_ValueEnd[1]
			self.assertGreater(c_PriorityW, c_PriorityR)
			self.assertGreater(c_PriorityW, c_PriorityF)
			self.assertGreater(c_PriorityF, c_PriorityR)

if __name__ == '__main__':
	unittest.main(failfast=False)

