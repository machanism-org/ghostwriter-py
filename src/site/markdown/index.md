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

`mgw` is a Python package that exposes the Machai Ghostwriter command-line
processor to Python applications and shell users. It solves the integration
problem of invoking a Java-based processor from Python by packaging the
Ghostwriter runtime with the Python distribution and using JPype to start a
JVM lazily. Callers can therefore use Ghostwriter without assembling a Java
class path themselves, while retaining both a familiar CLI and a small Python
API.

## Introduction

The wrapper provides three entry points for the same Ghostwriter runtime:

- The installed `mgw` console command forwards command-line arguments.
- `python -m mgw` provides the equivalent module entry point.
- The `gw` Python function accepts an argument list and returns the Java
  processor's result as a string.

The implementation also exposes `gdp` for direct guidance processing and `adw`
for executing an Act. These functions construct the corresponding Java
processor and convert Java collection results into ordinary Python lists. The
package initializer resolves public functions lazily, so importing `mgw` does
not start the JVM or eagerly load JPype. On first use, the bridge validates
`JAVA_HOME`, verifies that JPype can locate a JVM library, adds the packaged
`ghostwriter.jar` to the class path, and starts the JVM with string conversion
enabled. The JVM is reused for subsequent calls because JPype cannot restart a
JVM after it has been shut down.

The package targets Python 3.9 and newer and declares `jpype1>=1.4.0` as a
runtime dependency. The bundled runtime is included in the wheel through the
Hatchling build configuration, while the Maven release build assembles that
runtime into the Python package.

## Project Structure

The project is organized as a small Python-to-Java bridge:

- The **public interface layer** provides lazy exports, the `mgw` console
  script, and the `python -m mgw` module entry point.
- The **JVM bridge layer** validates the Java environment, resolves the
  packaged runtime relative to the Python installation, starts JPype, and
  forwards command-line or structured processor requests. It also validates
  `JAVA_HOME` and converts Java collection results into Python lists.
- The **Ghostwriter runtime layer** supplies the Java command-line processor
  and the guidance and Act processors used by the Python API. The runtime is
  loaded by the JVM only when an operation is first requested.
- The **packaging layer** builds the Java runtime with Maven and includes it in
  the Python wheel and source distribution so users install one package.

A CLI user or Python application invokes the Python interface. The bridge then
loads the bundled Java runtime in the Java Virtual Machine and returns either a
text result from `gw` or a Python list from `gdp` and `adw`.

![C4 Project Diagram](./images/c4-diagram.png)

## Installation and Prerequisites

Use Python 3.9 or newer, install the package with a Python package installer,
and provide a Java installation supported by JPype. **`JAVA_HOME` must be
defined** and must point to an existing JDK or JVM installation before calling
any wrapper operation. The bridge also requires JPype to find a valid JVM
library and the installed package to contain the bundled Ghostwriter runtime.

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

Import the public `gw` function and pass the argument list intended for
Ghostwriter:

```python
from mgw import gw

result = gw(["--help"])
print(result)
```

`gw` does not parse or rewrite the supplied arguments. When called without an
argument list, it forwards the current process arguments after the executable
name. The JVM starts on the first call and is reused for later calls in the
same process.

### Direct guidance processing

Use `gdp` when an application needs to process guidance tags directly. It
accepts a project directory and path, along with optional model, configuration,
traversal, exclusion, thread, and timeout settings:

```python
from mgw.ghostwriter import gdp

report = gdp(path="src", project_dir=".")
for item in report:
    print(item)
```

`gdp` creates a Java `GuidanceProcessor`, scans the requested path, and returns
its report as a Python list. `threads` must be a positive integer when supplied;
`excludes` is a list of path patterns; and `module_thread_timeout_minutes` must
also be positive. `non_recursive` controls traversal depth.

### Act execution

Use `adw` with a non-empty Act name or expression:

```python
from mgw import adw

results = adw("my-act", path="src", project_dir=".")
```

`adw` constructs an `ActProcessor`, optionally applies the model,
configuration, Act location, interactive mode, and normal-order settings, scans
the requested path, and returns the processor results as a Python list.

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
- `jpype1>=1.4.0`.
- A supported Java runtime with **`JAVA_HOME` defined**.
- The bundled Ghostwriter runtime included in the installed package.

## License

Apache License, Version 2.0.
