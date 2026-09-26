<!-- @guidance: 
- This is the README.md file for the PyPI release. It should be concise and contain all the necessary information and follow best practices.
- Add link to the project site: https://machai.machanism.org/ghostwriter-py/
- License: Apache License, Version 2.0.
-->

# `mgw`

Python wrapper for the [Machai Ghostwriter](https://machai.machanism.org/ghostwriter-py/) command-line processor. The package bundles the Ghostwriter Java runtime and uses [JPype](https://jpype.readthedocs.io/) to run it.

## Requirements

- Python 3.9 or newer
- Java runtime discoverable by JPype (setting `JAVA_HOME` is recommended)

JPype1 is installed automatically as a package dependency.

## Installation

```bash
python -m pip install mgw
```

## Usage

Use the installed command-line entry point:

```bash
mgw --help
```

You can also invoke the package as a module:

```bash
python -m mgw --help
```

From Python, pass the arguments intended for Ghostwriter to `gw`:

```python
from mgw.__main__ import gw

result = gw(["--help"])
print(result)
```

Arguments are forwarded directly to Ghostwriter. The Java Virtual Machine starts on the first call and is reused for subsequent calls in the same process.

## Project site

[https://machai.machanism.org/ghostwriter-py/](https://machai.machanism.org/ghostwriter-py/)

## License

Apache License, Version 2.0. See the project repository for the full license text.
