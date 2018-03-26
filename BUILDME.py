#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This is an entry point for the file BUILDME."""

# The current file:
#     Should be named "BUILDME.py"
#     Should be present in the project root folder

import sys


def main(p_args):
	"""Entry point."""
	import subprocess
	c_args = [sys.executable, "-B", "BUILDME"]
	c_args.extend(p_args)
	return subprocess.call(c_args)


if '__main__' == __name__:
	sys.dont_write_bytecode = True
	sys.exit(main(sys.argv[1:]))
