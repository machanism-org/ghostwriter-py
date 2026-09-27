<!-- @guidance: >>> ${guidances}/index-content.md 
This is a python wraper of ghostwriter cli.

- Add ![PyPI Version](https://img.shields.io/pypi/v/mgw)
- Add ![Test PyPI Version](https://img.shields.io/pypi/v/mgw?pypiBaseUrl=https%3A%2F%2Ftest.pypi.org&style=flat&label=test.pypi)
- Analyze `src/main/python` python project and detailed describe it in this readme file.
- no maven-central shields required.
- JAVA_HOME should be defined.
--> 

# Ghostwriter Python Wrapper (`mgw`)

[![PyPI Version](https://img.shields.io/pypi/v/mgw)](https://pypi.org/project/mgw) [![Test PyPI Version](https://img.shields.io/pypi/v/mgw?pypiBaseUrl=https%3A%2F%2Ftest.pypi.org&style=flat&label=test.pypi)](https://test.pypi.org/project/mgw)

`mgw` is a Python package and command-line wrapper for the Machai Ghostwriter
Java processor. It packages the Ghostwriter runtime with the Python
installation and uses JPype to start a JVM lazily, so Python applications and
shell users can invoke Ghostwriter without assembling a Java class path. The
wrapper preserves the Java processor's argument handling while also exposing
Python functions for guidance processing and Act execution.

## Introduction

The package provides one runtime through three convenient interfaces:

- The installed `mgw` console command forwards command-line arguments.
- `python -m mgw` provides the equivalent module entry point.
- The `gw` function accepts an argument list, invokes Ghostwriter, and returns
  its result as a string.

The `gdp` function exposes direct guidance processing, and `adw` executes an
Act. Both APIs return Java collection results as ordinary Python lists and
accept project paths plus processor options. The package's public initializer
resolves its public functions lazily, avoiding JVM startup and JPype loading
until an operation is requested.

On first use, the bridge validates `JAVA_HOME`, checks that JPype can locate a
JVM library, loads the packaged Ghostwriter runtime, and starts the JVM with
string conversion enabled. The JVM remains available for subsequent calls in
the same process because JPype does not support restarting a stopped JVM.
Optional local libraries or Maven coordinates can be supplied to the direct
processor APIs and are resolved only when needed.

The package targets Python 3.9 and newer. Its runtime dependencies are
`jpype1>=1.4.0` and `jgo>=1.0.0`; the latter resolves optional Maven libraries.
The release build assembles the Java runtime and Hatchling includes it in the
Python wheel and source distribution, allowing users to install one package.

## Project Structure

This is a small Python-to-Java bridge with four cooperating layers:

- The **public interface layer** provides lazy Python exports, the console
  entry point, and the module entry point.
- The **JVM bridge layer** validates the Java environment, resolves the
  packaged runtime and optional libraries, starts JPype, and forwards requests.
- The **processor API layer** maps Python arguments to Ghostwriter's command,
  guidance, and Act processors, including traversal, exclusions, thread, and
  timeout settings.
- The **packaging layer** builds the Java runtime and embeds it in the Python
  distribution so the installed package is self-contained.

A CLI user or Python application invokes the Python interface. The bridge then
loads the bundled Java runtime in the JVM and returns either the text result of
`gw` or a Python list from `gdp` and `adw`.

![C4 Project Diagram](./images/c4-diagram.png)

## Installation and Prerequisites

Use Python 3.9 or newer, install the package with a Python package installer,
and provide a supported Java installation. **`JAVA_HOME` must be defined** and
must point to an existing JDK or JVM installation before calling any wrapper
operation. JPype must also be able to find a valid JVM library, and the
installed package must contain the bundled Ghostwriter runtime.

On Windows PowerShell:

```powershell
$env:JAVA_HOME = "C:\Path\To\Your\JDK"
$env:Path = "$env:JAVA_HOME\bin;$env:Path"
python -m pip install mgw
```

For a local checkout, build the Java runtime and install the Python package:

```powershell
mvn clean package -Prelease
python -m pip install .\src\main\python
```

## Usage

### Console command

Pass Ghostwriter arguments directly to the installed console command:

```powershell
mgw --help
```

### Python module

The same command-line interface is available as a module:

```powershell
python -m mgw --help
```

### `gw` Python API

Pass the argument list intended for Ghostwriter to the public function:

```python
from mgw import gw

result = gw(["--help"])
print(result)
```

`gw` does not parse or rewrite the supplied arguments. If no argument list is
provided, it forwards the current process arguments after the executable name.
The JVM starts on the first call and is reused for later calls in that process.

### Direct guidance processing

Use `gdp` when an application needs to process guidance tags directly. It
accepts a project directory and path, together with optional model,
configuration, traversal, exclusion, thread, timeout, and library settings:

```python
from mgw.ghostwriter import gdp

report = gdp(path="src", project_dir=".", threads=2)
for item in report:
    print(item)
```

`gdp` creates a guidance processor, scans the requested path, and returns its
report as a Python list. `threads` and
`module_thread_timeout_minutes` must be positive integers when supplied;
`excludes` must be a list of path patterns; and `non_recursive` controls
traversal depth. `libs` may contain existing library paths or Maven
coordinates and must be a list rather than a string.

### Act execution

Use `adw` with a non-empty Act name or expression:

```python
from mgw import adw

results = adw("my-act", path="src", project_dir=".")
for result in results:
    print(result)
```

`adw` constructs an Act processor, optionally applies the model,
configuration, Act location, interactive mode, normal-order setting, and
additional libraries, scans the requested path, and returns the processor
results as a Python list.

## Building

From the project root, assemble the Java runtime and build the Python source
distribution and wheel:

```powershell
mvn clean package -Prelease
Set-Location src/main/python
python -m pip install --upgrade build
python -m build
```

The Python artifacts are written to the `dist` directory. The release profile
places the assembled runtime in the package, and Hatchling's wheel
configuration includes it at installation time.

## Requirements

- Python 3.9 or newer.
- `jpype1>=1.4.0` and `jgo>=1.0.0`.
- A supported Java runtime with **`JAVA_HOME` defined**.
- The bundled Ghostwriter runtime included in the installed package.

## License

Apache License, Version 2.0.
