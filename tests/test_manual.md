# Manual tests

## Validate  Published source tar file.

### Act
1. Download source tar.gz file from pypi

	https://pypi.org/project/readerwriterlock/#files

2. Extract its content in a folder

3. browse to the __extracted folder__/readerwriterlock

4. From a command prompt:

```bash
python3 -m pip uninstall readerwriterlock typing_extensions;
python3 -m pip install .;
python3 -c "from readerwriterlock import rwlock";
python3 -m pip uninstall readerwriterlock;
```

### Assert

1.
```bash
python3 -c "from readerwriterlock import rwlock; rwlock.RWLockFair().gen_wlock().acquire();"
```

## Validate Published binary whl file.

### Arrange
1. Make sure readerwriterlock is not already installed

```bash
python3 -m pip uninstall readerwriterlock typing_extensions
```

### Act
1. Download binary whl file from pypi

	https://pypi.org/project/readerwriterlock/#files

```bash
python3 -m pip install readerwriterlock-#.#.#.whl
```

### Assert

1.
```bash
python3 -c "import readerwriterlock; readerwriterlock.RWLockFair().gen_wlock().acquire();"
```
