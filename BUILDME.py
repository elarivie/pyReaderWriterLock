#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This is an entry point for the file BUILDME
# The current file:
#     Should be named "BUILDME.py"
#     Should be present in the project root folder

def main(p_Args):
	import os
	import subprocess
	import sys
	c_Args = [sys.executable, "-B", "BUILDME"]
	c_Args.extend(p_Args)
	return subprocess.call(c_Args)

if __name__ == '__main__':
	import sys
	sys.dont_write_bytecode = True
	sys.exit(main(sys.argv[1:]))

