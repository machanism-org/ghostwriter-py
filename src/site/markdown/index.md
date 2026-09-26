<!-- @guidance: >>> ${guidances}/index-content.md 
This is a python wraper of ghostwriter cli.

- Analyze `src/main/python` python project and detailed describe it in this readme file.
- no maven-central shields required.
- JAVA_HOME should be defined.
--> 

# Ghostwriter Python Wrapper (`mgw`)

`mgw` is a Python wrapper for the Machai Ghostwriter command-line processor. It
provides a Python API, an installed console command, and a module entry point
while packaging the Java Ghostwriter runtime alongside the Python distribution.
The wrapper removes the need for callers to configure a Java class path
manually: it locates the bundled runtime relative to the installed package and
uses JPype to invoke the Java processor.

## Introduction

The project bridges a Python packaging and command-line experience with the
Ghostwriter Java implementation. Its goal is to let Python applications and
shell users invoke Ghostwriter with the same argument sequence while keeping
the Java runtime self-contained in the installed package.

The Python package targets Python 3.9 or newer and depends on `jpype1>=1.4.0`.
Its public `gw` function accepts an optional `list[str]`; when no list is
provided, it forwards the current process arguments after the executable name.
On first use, the wrapper discovers the JVM, starts it with string conversion
enabled, adds the bundled Ghostwriter runtime to the class path, and invokes
`org.machanism.machai.gw.processor.Ghostwriter.main`. Subsequent calls reuse the
same JVM, as JPype does not support restarting a JVM after shutdown.

The package initializer exposes `gw` lazily, and the module implementation owns
argument forwarding, JVM startup, runtime resolution, and result handling. The
Maven build assembles the Java runtime into the Python package, while Hatchling
builds the Python source distribution and wheel with that runtime included.

## Project Structure

The project consists of three cooperating layers. The Python package layer
provides the public API and command-line entry points, resolves the embedded
runtime relative to the installation, and forwards arguments. The Java
execution layer supplies the Ghostwriter processor that performs the requested
command-line work and returns its result. The build and packaging layer
assembles the Java runtime and includes it in the Python distribution, so users
can install one package rather than manage a separate class path.

![C4 Project Diagram](./images/c4-diagram.png)

## Installation and Prerequisites

Use Python 3.9 or newer, a Java installation supported by JPype, and a working
Python package installer. **`JAVA_HOME` must be defined** before running the
wrapper and should point to a JDK or JVM installation. On Windows PowerShell,
for example:

```powershell
$env:JAVA_HOME = "C:\Path\To\Your\JDK"
$env:Path = "$env:JAVA_HOME\bin;$env:Path"
python -m pip install mgw
```

For a local checkout, install the package after building the Java runtime:

```powershell
mvn clean package -Prelease
python -m pip install .\src\main\python
```

The package declares JPype as a dependency. JPype must be able to discover the
JVM at `jpype.getDefaultJVMPath()`, and the installed package must contain the
bundled Ghostwriter runtime.

## Usage

### Console command

Pass Ghostwriter arguments directly to the installed `mgw` command:

```powershell
mgw --help
```

### Python module

The package can also be run as a module:

```powershell
python -m mgw --help
```

### Python API

Import `gw` and pass the argument list intended for Ghostwriter:

```python
from mgw.__main__ import gw

result = gw(["--help"])
print(result)
```

Arguments are forwarded without Python-side command-line parsing. The JVM is
started lazily on the first call and reused by later calls in the same process.
The function returns the result produced by the Java processor as a Python
string.

## Building

From the project root, assemble the Java runtime and build the Python
artifacts:

```powershell
mvn clean package -Prelease
Set-Location src/main/python
python -m pip install --upgrade build
python -m build
```

The generated source distribution and wheel are placed in the Python
project's `dist` directory. The Maven release profile assembles the Java
runtime, and the Python wheel configuration includes it with the package.

## Requirements

- Python 3.9 or newer.
- `jpype1>=1.4.0`.
- A supported Java runtime with **`JAVA_HOME` defined**.
- The bundled Ghostwriter runtime, included in the installed package.

## License

Apache License, Version 2.0.
