<!-- @guidance: >>> ${guidances}/index-content.md 
This is a python wraper of ghostwriter cli.

- Add ![PyPI Version](https://img.shields.io/pypi/v/mgw)
- Analyze `src/main/python` python project and detailed describe it in this readme file.
- no maven-central shields required.
- JAVA_HOME should be defined.
--> 

# Ghostwriter Python Wrapper (`mgw`)

![PyPI Version](https://img.shields.io/pypi/v/mgw)

`mgw` is a Python package that lets Python applications and shell users invoke
the Machai Ghostwriter command-line processor. It combines a small Python
interface with the bundled Java Ghostwriter runtime, so an installation does
not require callers to assemble a Java class path manually.

## Introduction

The wrapper provides three ways to use Ghostwriter: the `mgw` console command,
the `python -m mgw` module entry point, and Python functions for direct
integration. It uses JPype to start a JVM lazily, adds the packaged Ghostwriter
runtime to that JVM, forwards the requested arguments or processing options,
and converts Java collection results to ordinary Python lists where applicable.
The JVM is reused for subsequent calls because JPype does not support starting
a JVM again after it has been shut down.

The package targets Python 3.9 and newer and declares `jpype1>=1.4.0` as a
runtime dependency. Its package interface lazily exposes `gw` and `adw`, while
the implementation also provides `gdp` for direct guidance processing. `gw`
invokes the Java `org.machanism.machai.gw.processor.Ghostwriter` entry point and
returns its result as a string. `gdp` constructs a Java `GuidanceProcessor`,
scans a project for guidance tags, and returns its report as a Python list;
`adw` constructs an `ActProcessor`, executes a named Act, and returns its
results as a Python list. Before starting the JVM, each operation requires a
defined, existing `JAVA_HOME` and a JVM library discoverable by JPype.

## Project Structure

The project has a Python package layer, a Java bridge layer, and a bundled
runtime layer. The package layer supplies lazy public exports and the installed
console and module entry points. The bridge validates the Java environment,
starts JPype only when needed, resolves the packaged runtime, and delegates
command-line, guidance, and Act requests to the appropriate Java processors.
The runtime layer contains the Ghostwriter processor and its dependencies in
the distribution. External Python and Java runtimes host these layers, while a
CLI user or Python application initiates processing and receives text or
ordinary Python lists.

![C4 Project Diagram](./images/c4-diagram.png)

## Installation and Prerequisites

Use Python 3.9 or newer, install the package with a Python package installer,
and provide a Java installation supported by JPype. **`JAVA_HOME` must be
defined** and must point to an existing JDK or JVM installation before invoking
any wrapper function. On Windows PowerShell:

```powershell
$env:JAVA_HOME = "C:\Path\To\Your\JDK"
$env:Path = "$env:JAVA_HOME\bin;$env:Path"
python -m pip install mgw
```

The wrapper checks that `JAVA_HOME` exists and that JPype can locate the JVM
library. It also expects the installed package to contain the bundled
Ghostwriter runtime.

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

### Python API

Import the public `gw` function and pass the argument list intended for
Ghostwriter:

```python
from mgw import gw

result = gw(["--help"])
print(result)
```

When called without an argument list, `gw()` forwards the current process
arguments after the executable name. The JVM starts on the first call and is
reused for later calls in the same process.

For direct guidance processing, use `gdp` with an optional project directory,
path, model, configuration file, and processor settings:

```python
from mgw.ghostwriter import gdp

report = gdp(path="src", project_dir=".")
```

To execute an Act, use `adw` with a non-empty Act name or expression:

```python
from mgw import adw

results = adw("my-act", path="src", project_dir=".")
```

Both functions return Python lists. Their optional settings include the model,
configuration file, path matcher, Act location, interactive mode, exclusions,
thread count, non-recursive traversal, and module timeout; these are forwarded
to the corresponding Java processor after JVM startup.

## Building

From the project root, assemble the Java runtime and build the Python
artifacts:

```powershell
mvn clean package -Prelease
Set-Location src/main/python
python -m pip install --upgrade build
python -m build
```

The source distribution and wheel are written to the Python project's `dist`
directory. The release build places the Java runtime alongside the Python
package, and Hatchling includes it in the wheel.

## Requirements

- Python 3.9 or newer.
- `jpype1>=1.4.0`.
- A supported Java runtime with **`JAVA_HOME` defined**.
- The bundled Ghostwriter runtime included in the installed package.

## License

Apache License, Version 2.0.
