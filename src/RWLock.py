#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Read Write Lock
"""

import threading
import time

class RWLockRead(object):
	"""
		A Read/Write lock giving preference to Reader
	"""
	def __init__(self):
		self.V_ReadCount = 0
		self.A_Resource = threading.Lock()
		self.A_LockReadCount = threading.Lock()
	class _aReader(object):
		def __init__(self, p_RWLock):
			self.A_RWLock = p_RWLock
			self.V_Locked = False

		def acquire(self, blocking=1, timeout=-1):
			p_TimeOut = None if (blocking and timeout < 0) else (timeout if blocking else 0)
			c_DeadLine = None if p_TimeOut is None else (time.time() + p_TimeOut)
			if not self.A_RWLock.A_LockReadCount.acquire(blocking=1, timeout=-1 if c_DeadLine is None else max(0, c_DeadLine - time.time())):
				return False
			self.A_RWLock.V_ReadCount += 1
			if self.A_RWLock.V_ReadCount == 1:
				if not self.A_RWLock.A_Resource.acquire(blocking=1, timeout=-1 if c_DeadLine is None else max(0, c_DeadLine - time.time())):
					self.A_RWLock.V_ReadCount -= 1
					self.A_RWLock.A_LockReadCount.release()
					return False
			self.A_RWLock.A_LockReadCount.release()
			self.V_Locked = True
			return True

		def release(self):
			if not self.V_Locked: raise RuntimeError("cannot release un-acquired lock")
			self.V_Locked = False
			self.A_RWLock.A_LockReadCount.acquire()
			self.A_RWLock.V_ReadCount -= 1
			if self.A_RWLock.V_ReadCount == 0:
				self.A_RWLock.A_Resource.release()
			self.A_RWLock.A_LockReadCount.release()
		def locked(self):
			return self.V_Locked
		def __enter__(self):
			self.acquire()
		def __exit__(self, p_Type, p_Value, p_Traceback):
			self.release()
	class _aWriter(object):
		def __init__(self, p_RWLock):
			self.A_RWLock = p_RWLock
			self.V_Locked = False
		def acquire(self, blocking=1, timeout=-1):
			self.V_Locked = self.A_RWLock.A_Resource.acquire(blocking, timeout)
			return self.V_Locked
		def release(self):
			if not self.V_Locked: raise RuntimeError("cannot release un-acquired lock")
			self.V_Locked = False
			self.A_RWLock.A_Resource.release()
		def locked(self):
			return self.V_Locked
		def __enter__(self):
			self.acquire()
		def __exit__(self, p_Type, p_Value, p_Traceback):
			self.release()
	def genRlock(self):
		"""
			Generate a reader lock
		"""
		return RWLockRead._aReader(self)
	def genWlock(self):
		"""
			Generate a writer lock
		"""
		return RWLockRead._aWriter(self)

class RWLockWrite(object):
	"""
		A Read/Write lock giving preference to Writer
	"""
	def __init__(self):
		self.V_ReadCount = 0
		self.V_WriteCount = 0
		self.A_LockReadCount = threading.Lock()
		self.A_LockWriteCount = threading.Lock()
		self.A_LockReadEntry = threading.Lock()
		self.A_LockReadTry = threading.Lock()
		self.A_Resource = threading.Lock()
	class _aReader(object):
		def __init__(self, p_RWLock):
			self.A_RWLock = p_RWLock
			self.V_Locked = False
		def acquire(self, blocking=1, timeout=-1):
			p_TimeOut = None if (blocking and timeout < 0) else (timeout if blocking else 0)
			c_DeadLine = None if p_TimeOut is None else (time.time() + p_TimeOut)
			if not self.A_RWLock.A_LockReadEntry.acquire(blocking=1, timeout=-1 if c_DeadLine is None else max(0, c_DeadLine - time.time())):
				return False
			if not self.A_RWLock.A_LockReadTry.acquire(blocking=1, timeout=-1 if c_DeadLine is None else max(0, c_DeadLine - time.time())):
				self.A_RWLock.A_LockReadEntry.release()
				return False
			if not self.A_RWLock.A_LockReadCount.acquire(blocking=1, timeout=-1 if c_DeadLine is None else max(0, c_DeadLine - time.time())):
				self.A_RWLock.A_LockReadTry.release()
				self.A_RWLock.A_LockReadEntry.release()
				return False
			self.A_RWLock.V_ReadCount += 1
			if (self.A_RWLock.V_ReadCount == 1):
				if not self.A_RWLock.A_Resource.acquire(blocking=1, timeout=-1 if c_DeadLine is None else max(0, c_DeadLine - time.time())):
					self.A_RWLock.A_LockReadTry.release()
					self.A_RWLock.A_LockReadEntry.release()
					self.A_RWLock.V_ReadCount -= 1
					self.A_RWLock.A_LockReadCount.release()
					return False
			self.A_RWLock.A_LockReadCount.release()
			self.A_RWLock.A_LockReadTry.release()
			self.A_RWLock.A_LockReadEntry.release()
			self.V_Locked = True
			return True
		def release(self):
			if not self.V_Locked: raise RuntimeError("cannot release un-acquired lock")
			self.V_Locked = False
			self.A_RWLock.A_LockReadCount.acquire()
			self.A_RWLock.V_ReadCount -= 1
			if (self.A_RWLock.V_ReadCount == 0):
				self.A_RWLock.A_Resource.release()
			self.A_RWLock.A_LockReadCount.release()
		def locked(self):
			return self.V_Locked
		def __enter__(self):
			self.acquire()
		def __exit__(self, p_Type, p_Value, p_Traceback):
			self.release()
	class _aWriter(object):
		def __init__(self, p_RWLock):
			self.A_RWLock = p_RWLock
			self.V_Locked = False
		def acquire(self, blocking=1, timeout=-1):
			p_TimeOut = None if (blocking and timeout < 0) else (timeout if blocking else 0)
			c_DeadLine = None if p_TimeOut is None else (time.time() + p_TimeOut)
			if not self.A_RWLock.A_LockWriteCount.acquire(blocking=1, timeout=-1 if c_DeadLine is None else max(0, c_DeadLine - time.time())):
				return False
			self.A_RWLock.V_WriteCount += 1
			if (self.A_RWLock.V_WriteCount == 1):
				if not self.A_RWLock.A_LockReadTry.acquire(blocking=1, timeout=-1 if c_DeadLine is None else max(0, c_DeadLine - time.time())):
					self.A_RWLock.V_WriteCount -= 1
					self.A_RWLock.A_LockWriteCount.release()
					return False
			self.A_RWLock.A_LockWriteCount.release()
			if not self.A_RWLock.A_Resource.acquire(blocking=1, timeout=-1 if c_DeadLine is None else max(0, c_DeadLine - time.time())):
				self.A_RWLock.A_LockWriteCount.acquire()
				self.A_RWLock.V_WriteCount -= 1
				if self.A_RWLock.V_WriteCount == 0:
					self.A_RWLock.A_LockReadTry.release()
				self.A_RWLock.A_LockWriteCount.release()
				return False
			self.V_Locked = True
			return True
		def release(self):
			if not self.V_Locked: raise RuntimeError("cannot release un-acquired lock")
			self.V_Locked = False
			self.A_RWLock.A_Resource.release()
			self.A_RWLock.A_LockWriteCount.acquire()
			self.A_RWLock.V_WriteCount -= 1
			if (self.A_RWLock.V_WriteCount == 0):
				self.A_RWLock.A_LockReadTry.release()
			self.A_RWLock.A_LockWriteCount.release()
		def locked(self):
			return self.V_Locked
		def __enter__(self):
			self.acquire()
		def __exit__(self, p_Type, p_Value, p_Traceback):
			self.release()
	def genRlock(self):
		"""
			Generate a reader lock
		"""
		return RWLockWrite._aReader(self)
	def genWlock(self):
		"""
			Generate a writer lock
		"""
		return RWLockWrite._aWriter(self)

class RWLockFair(object):
	"""
		A Read/Write lock giving fairness to both Reader and Writer
	"""
	def __init__(self):
		self.V_ReadCount = 0
		self.A_LockReadCount = threading.Lock()
		self.A_LockRead = threading.Lock()
		self.A_LockWrite = threading.Lock()
	class _aReader(object):
		def __init__(self, p_RWLock):
			self.A_RWLock = p_RWLock
			self.V_Locked = False
		def acquire(self, blocking=1, timeout=-1):
			p_TimeOut = None if (blocking and timeout < 0) else (timeout if blocking else 0)
			c_DeadLine = None if p_TimeOut is None else (time.time() + p_TimeOut)
			if not self.A_RWLock.A_LockRead.acquire(blocking=1, timeout=-1 if c_DeadLine is None else max(0, c_DeadLine - time.time())):
				return False
			if not self.A_RWLock.A_LockReadCount.acquire(blocking=1, timeout=-1 if c_DeadLine is None else max(0, c_DeadLine - time.time())):
				self.A_RWLock.A_LockRead.release()
				return False
			self.A_RWLock.V_ReadCount += 1
			if self.A_RWLock.V_ReadCount == 1:
				if not self.A_RWLock.A_LockWrite.acquire(blocking=1, timeout=-1 if c_DeadLine is None else max(0, c_DeadLine - time.time())):
					self.A_RWLock.V_ReadCount -= 1
					self.A_RWLock.A_LockReadCount.release()
					self.A_RWLock.A_LockRead.release()
					return False
			self.A_RWLock.A_LockReadCount.release()
			self.A_RWLock.A_LockRead.release()
			self.V_Locked = True
			return True
		def release(self):
			if not self.V_Locked: raise RuntimeError("cannot release un-acquired lock")
			self.V_Locked = False
			self.A_RWLock.A_LockReadCount.acquire()
			self.A_RWLock.V_ReadCount -= 1
			if self.A_RWLock.V_ReadCount == 0:
				self.A_RWLock.A_LockWrite.release()
			self.A_RWLock.A_LockReadCount.release()
		def locked(self):
			return self.V_Locked
		def __enter__(self):
			self.acquire()
		def __exit__(self, p_Type, p_Value, p_Traceback):
			self.release()
	class _aWriter(object):
		def __init__(self, p_RWLock):
			self.A_RWLock = p_RWLock
			self.V_Locked = False
		def acquire(self, blocking=1, timeout=-1):
			p_TimeOut = None if (blocking and timeout < 0) else (timeout if blocking else 0)
			c_DeadLine = None if p_TimeOut is None else (time.time() + p_TimeOut)
			if not self.A_RWLock.A_LockRead.acquire(blocking=1, timeout=-1 if c_DeadLine is None else max(0, c_DeadLine - time.time())):
				return False
			if not self.A_RWLock.A_LockWrite.acquire(blocking=1, timeout=-1 if c_DeadLine is None else max(0, c_DeadLine - time.time())):
				self.A_RWLock.A_LockRead.release()
				return False
			self.V_Locked = True
			return True
		def release(self):
			if not self.V_Locked: raise RuntimeError("cannot release un-acquired lock")
			self.V_Locked = False
			self.A_RWLock.A_LockWrite.release()
			self.A_RWLock.A_LockRead.release()
		def locked(self):
			return self.V_Locked
		def __enter__(self):
			self.acquire()
		def __exit__(self, p_Type, p_Value, p_Traceback):
			self.release()
	def genRlock(self):
		"""
			Generate a reader lock
		"""
		return RWLockFair._aReader(self)
	def genWlock(self):
		"""
			Generate a writer lock
		"""
		return RWLockFair._aWriter(self)

