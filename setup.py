"""Setup."""

import pathlib
from setuptools import setup, find_packages  # type: ignore [import]


def read(fname: str) -> str:
	"""Get the content of a file at the root of the project."""
	return pathlib.Path(pathlib.Path(__file__).parent, fname).read_text(encoding="utf-8").strip()


setup(
	name=read("NAME"),
	packages=find_packages(),
	version=read("VERSION"),
	author="Éric Larivière",
	author_email="ericlariviere@hotmail.com",
	maintainer="Éric Larivière",
	url="https://github.com/elarivie/pyReaderWriterLock",
	download_url="https://github.com/elarivie/pyReaderWriterLock",
	description="A python implementation of the three Reader-Writer problems.",
	long_description_content_type="text/markdown",
	long_description=read("README.md"),
	license="MIT",
	keywords=["rwlock", "read-write lock", "lock", "priority", "reader", "writer", "fair", "read", "write", "thread", "synchronize"],
	classifiers=[
		# How mature is this project? Common values are
		# 3 - Alpha
		# 4 - Beta
		# 5 - Production/Stable
		"Development Status :: 5 - Production/Stable",

		# Indicate who your project is intended for
		"Intended Audience :: Developers",

		# Pick your license as you wish (should match "license" above)
		"License :: OSI Approved :: MIT License",

		# Specify the Python versions supported here:
		"Programming Language :: Python :: 3.7",
		"Programming Language :: Python :: 3.8",
		"Programming Language :: Python :: 3.9"
	],
	project_urls={
		"Source": "https://github.com/elarivie/pyReaderWriterLock",
		"Tracker": "https://github.com/elarivie/pyReaderWriterLock/issues"
	},
	install_requires=["typing_extensions"],
	python_requires=">=3.6",
	zip_safe=False,
	package_data={"readerwriterlock": ["py.typed"]}
)
