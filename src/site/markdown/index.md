<!-- @guidance: >>> ${guidances}/readme-content.md 
This is a python wraper of ghostwriter cli.

- Analyze `src/main/python` python project and detailed describe it in this readme file.
- Insert the image of the project structure diagram by the path: `./images/c4-diagram.png` (`src/site/puml/c4-diagram.puml`).
- no maven-central shields required.
- JAVA_HOME should be defined.
-->

# Ghostwriter Python Wrapper (`mgw`)

## Cloning and Getting Started

To clone and set up this project locally, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/machanism-org/ghostwriter-py.git
   cd ghostwriter-py
   ```
2. **Build the project using Maven:**
   ```bash
   mvn clean install
   ```

A Python package that provides a thin interface to the Machai Ghostwriter command-line processor. It targets Python 3.9 or newer, exposes an `mgw` console command, and packages the Ghostwriter Java runtime as a wheel resource. JPype starts a JVM lazily, loads that runtime, forwards Ghostwriter arguments, and returns the Java processor result to Python.

## Introduction

The Python project under `src/main/python` contains the `mgw` package and its Hatch build configuration. The package declares `jpype1>=1.4.0`, requires Python 3.9 or newer, and defines the `mgw` console entry point. The wheel configuration also includes `mgw/jars/ghostwriter.jar`, which is produced by the Maven build and supplies the Java command-line processor.

The wrapper implementation accepts an optional `list[str]`. If no list is provided, it forwards the process arguments after the executable name. On the first invocation it finds the bundled runtime relative to the installed package, starts JPype with string conversion enabled, and invokes the Ghostwriter Java processor. Subsequent calls reuse the running JVM; JPype does not support restarting a JVM after shutdown.

The package initializer is designed to lazily expose `gw`, while the module implementation provides the JVM startup and argument forwarding logic. In the current source tree, the initializer refers to a `ghostwriter` submodule that is not present, so callers should verify the package export before relying on `from mgw import gw`; the `mgw` console entry point is configured to call the implementation in the module entry point directly.

## Project Structure

![mgw component diagram](./images/c4-diagram.png)

The component design shows the following cooperating parts:

- **CLI user:** invokes the public Python API, the installed console command, or the Python module.
- **Public API:** is intended to lazily expose `gw` and delegate to the JVM bridge without eagerly starting the runtime.
- **JVM bridge and launcher:** accepts argument lists, resolves the bundled runtime, starts the JVM through JPype when necessary, forwards arguments, and returns the Java result.
- **Bundled Ghostwriter runtime:** supplies the Java processor that performs the command-line work.
- **Python and Java runtimes:** the Python runtime loads the package, while the Java runtime provides the JVM in which the processor executes.

The repository does not contain the requested diagram image, so a broken image link is intentionally omitted. The component relationships above provide the textual representation of the available design.

## Installation

Install the package in an environment with Python 3.9 or newer, JPype1, and a compatible Java runtime. **`JAVA_HOME` must be defined** before using the wrapper and should point to the JDK or JVM installation.

On Windows PowerShell, for example:

```powershell
$env:JAVA_HOME = "C:\Path\To\Your\JDK"
python -m pip install .
```

JPype must be able to discover a JVM through its default JVM-path lookup, and the packaged Ghostwriter runtime must be present in the installed package resources.

## Usage

Pass the same argument sequence that would be passed to the Ghostwriter CLI:

```python
from mgw import gw

result = gw(["--help"])
print(result)
```

After installation, use the console entry point directly:

```bash
mgw --help
```

The package can also be run as a module:

```bash
python -m mgw --help
```

Arguments are forwarded directly to Ghostwriter without Python-side command-line parsing. The JVM starts on the first invocation and is reused by later invocations in the same process.

## Building

From the project root, build the Java runtime and package artifacts with Maven:

```bash
mvn clean package
```

To build the Python source distribution and wheel independently:

```bash
python -m pip install --upgrade build
cd src/main/python
python -m build
```

The Maven assembly places the runtime archive in the Python package resources, and the Python wheel configuration forces that resource into the built wheel. Maven also invokes the Python build during the package phase.

## Requirements

- Python 3.9 or newer.
- JPype1 1.4.0 or newer.
- A compatible Java runtime with **`JAVA_HOME` defined**.
- A built Ghostwriter runtime included with the installed package.

## Project Site

[Machai Ghostwriter Python project site](https://machai.machanism.org/ghostwriter-py/)

## License

See the project metadata for the applicable Apache License, Version 2.0 terms.
