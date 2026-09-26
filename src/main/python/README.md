<!-- @guidance: 
- Review pytone project in `src/main/python`.
- This is the README.md file for the PyPI release. It should be concise and contain all the necessary information and follow best practices.
- Add link to the project site: https://machai.machanism.org/ghostwriter-py/
- License: Apache License, Version 2.0.
-->

# Ghostwriter Python Wrapper (`mgw`)

`mgw` is a Python wrapper for the Machai Ghostwriter command-line processor. It provides a Python API, a console command, and a module entry point while packaging the Java runtime in the Python distribution. JPype starts the JVM lazily and invokes the bundled Ghostwriter processor without requiring callers to configure a Java class path.

Project site: <https://machai.machanism.org/ghostwriter-py/>

## Cloning and Getting Started

To clone and set up this project locally:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/machanism-org/ghostwriter-py.git
   cd ghostwriter-py
   ```
2. **Build the project using Maven:**
   ```bash
   mvn clean install
   ```

## Introduction

The package targets Python 3.9 or newer and depends on `jpype1>=1.4.0`. Its public `gw` function accepts an optional `list[str]`; without an argument list, it forwards the current process arguments after the executable name. On first use, it discovers and starts the JVM with the bundled Ghostwriter JAR on the class path. Later calls reuse the JVM, since JPype does not support restarting one after shutdown.

The Python package supplies the public API and command-line entry points. The Java runtime supplies the Ghostwriter processor, and the Maven and Hatchling build configuration assembles and packages that runtime with the Python distribution.

## Project Structure

The project has three cooperating parts:

- **Python package:** exposes `gw`, provides the console and module entry points, resolves the bundled runtime, and forwards arguments.
- **Java runtime:** contains the Ghostwriter processor invoked through JPype.
- **Build and packaging:** assembles the Java runtime and includes it in the wheel and source distribution.

## Installation and Prerequisites

Use Python 3.9 or newer, a Java installation supported by JPype, and a Python package installer. `JAVA_HOME` must be defined and should point to a JDK or JVM installation. For example, in Windows PowerShell:

```powershell
$env:JAVA_HOME = "C:\Path\To\Your\JDK"
$env:Path = "$env:JAVA_HOME\bin;$env:Path"
python -m pip install mgw
```

For a local checkout, build the Java runtime before installing the package:

```powershell
mvn clean package -Prelease
python -m pip install .\src\main\python
```

JPype must be able to discover the JVM, and the installed package must contain the bundled Ghostwriter runtime.

## Usage

### Console command

```powershell
mgw --help
```

### Python module

```powershell
python -m mgw --help
```

### Python API

```python
from mgw import gw

result = gw(["--help"])
print(result)
```

Arguments are forwarded without Python-side command-line parsing. The function returns the result produced by the Java processor as a Python string.

## Building

From the project root, assemble the Java runtime and build the Python artifacts:

```powershell
mvn clean package -Prelease
Set-Location src/main/python
python -m pip install --upgrade build
python -m build
```

The generated wheel and source distribution are placed in `src/main/python/dist`.

## Requirements

- Python 3.9 or newer.
- `jpype1>=1.4.0`.
- A supported Java runtime with `JAVA_HOME` defined.
- The bundled Ghostwriter runtime, included in the installed package.

## License

Apache License, Version 2.0.
