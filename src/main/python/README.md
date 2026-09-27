<!-- @guidance: 
This is the README.md file for the PyPI release. It should be concise and contain all the necessary information and follow best practices.

- Title: Machai Ghostwriter Python Wrapper
- Review pytone project in `src/main/python`.
- Add link to the project site: https://machai.machanism.org/ghostwriter-py/
- License: Apache License, Version 2.0.
-->

# Machai Ghostwriter Python Wrapper

`mgw` is a Python wrapper for the Machai Ghostwriter command-line processor. It exposes a Python API, the `mgw` console command, and the `python -m mgw` entry point. The package includes the Java runtime and starts the JVM lazily through JPype.

Project site: <https://machai.machanism.org/ghostwriter-py/>

## Requirements

- Python 3.9 or newer.
- `jpype1>=1.4.0` (installed automatically with `mgw`).
- A Java installation supported by JPype, with `JAVA_HOME` set to its JDK or JVM installation.

## Installation

Install the release from PyPI:

```powershell
python -m pip install mgw
```

For a local checkout, build the Java runtime and install the Python package:

```powershell
mvn clean package -Prelease
python -m pip install .\src\main\python
```

The installed package contains the bundled Ghostwriter JAR, so callers do not need to configure a Java class path.

## Usage

Run the console command or module entry point:

```powershell
mgw --help
python -m mgw --help
```

Call the wrapper from Python:

```python
from mgw import gw

result = gw(["--help"])
print(result)
```

`gw` forwards arguments to Ghostwriter without Python-side command-line parsing and returns the processor result as a string. If called without an argument list, it forwards the current process arguments after the executable name. The JVM starts on first use and is reused for later calls.

The implementation module also exposes `gdp` for processing guidance tags and `adw` for executing an Act:

```python
from mgw.ghostwriter import adw, gdp

report = gdp(path="src")
results = adw("my-act", path="src")
```

## Building the Python distribution

After building the Java runtime, build the wheel and source distribution from the Python package directory:

```powershell
mvn clean package -Prelease
Set-Location src/main/python
python -m pip install --upgrade build
python -m build
```

Artifacts are written to `src/main/python/dist`.

## Project links

- Project site: <https://machai.machanism.org/ghostwriter-py/>
- Source repository: <https://github.com/machanism-org/ghostwriter-py>
- Issue tracker: <https://github.com/machanism-org/ghostwriter-py/issues>

## License

Apache License, Version 2.0.
