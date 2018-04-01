import os
from setuptools import setup, find_packages


def read(fname: str) -> str:
	"""Get the content of a file at the root of the project."""
	with open(os.path.join(os.path.dirname(__file__), fname), mode="r", encoding="utf-8") as file_stream:
		return file_stream.read().strip()


setup(
	metadata_version=2.1,
	name=read("NAME"),
	packages=find_packages(),
	version=read("VERSION"),
	author="Éric Larivière",
	maintainer="Éric Larivière",
	url="https://github.com/elarivie/pyReaderWriterLock",
	download_url="https://github.com/elarivie/pyReaderWriterLock",
	description=("A python implementation of the three Reader-Writer problems."),
	long_description=read('README.rst'),
	license='MIT',
	keywords=['rwlock', 'read-write lock', 'lock', "priority", "reader", "writer", "fair", "read", "write", "thread", "synchronize"],
	classifiers=[
		# How mature is this project? Common values are
		# 3 - Alpha
		# 4 - Beta
		# 5 - Production/Stable
		'Development Status :: 5 - Production/Stable',

		# Indicate who your project is intended for
		'Intended Audience :: Developers',

		# Pick your license as you wish (should match "license" above)
		'License :: OSI Approved :: MIT License',

		# Specify the Python versions you support here. In particular, ensure
		# that you indicate whether you support Python 2, Python 3 or both.
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6'
	],
	project_urls={
		'Source': 'https://github.com/elarivie/pyReaderWriterLock',
		'Tracker': 'https://github.com/elarivie/pyReaderWriterLock/issues'
	},
	install_requires=[],
	python_requires='>=3'
)
