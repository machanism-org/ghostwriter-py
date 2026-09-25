<!-- @guidance: >>> ${guidances}/readme-content.md 
This is a python wraper of ghostwriter cli.

- Analyze `machai.gw` python package and detailed describe it in this readme file.
- no maven-central shields required.
- JAVA_HOME should be defined.
-->

# Ghostwriter Python Wrapper (`gw-python`)

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

`gw-python` is a Python wrapper for the Machai Ghostwriter command-line processor. It
bundles the Ghostwriter Java runtime and exposes it through the `machai.gw` package,
using JPype to start an embedded JVM and invoke the Java implementation from Python.

## Introduction

The wrapper keeps the Ghostwriter runtime archive next to the Python package and
resolves its absolute path from the installed package location. Consumers therefore do
not need to configure a Java class path manually. The public `gw` function accepts a
list of command-line arguments, starts the JVM lazily on first use, invokes
`org.machanism.machai.gw.processor.Ghostwriter.main`, and returns the Java result as a
Python string.

The Java implementation remains responsible for Ghostwriter's command-line behavior;
the Python layer provides packaging, JVM startup, and argument forwarding rather than
reimplementing that behavior.

## The `machai.gw` Package

The Python distribution contains the `machai.gw` package and the bundled runtime archive
in its `jars` resource directory. Its main module defines the following public and
module-level symbols:

| Symbol | Kind | Description |
| --- | --- | --- |
| `BASE_DIR` | Module constant | Absolute path to the directory containing the wrapper module, computed from `__file__`. |
| `JAR_PATH` | Module constant | Absolute path to the bundled `jars/ghostwriter.jar`, resolved relative to `BASE_DIR`. |
| `gw(args: list[str]) -> str` | Function | Starts the JVM if necessary, places the bundled archive on its class path, imports `Ghostwriter`, invokes its static `main(args)` method, and returns the result. |

The module can also be run directly. In that mode, `sys.argv[1:]` is passed to `gw`, so
module invocation mirrors the underlying Ghostwriter command-line interface.

### Runtime behavior

- **Lazy JVM startup.** The JVM is created only when `gw()` is first called. Later calls
  reuse the running JVM. JPype does not support restarting a JVM after it has been
  shut down in the same process.
- **Self-contained artifact resolution.** The archive path is derived from the installed
  package location, so the current working directory does not affect discovery.
- **Transparent string conversion.** JPype is started with `convertStrings=True`, making
  the Java result available to callers as a native Python `str`.
- **Direct argument forwarding.** The supplied argument list is passed to the Java entry
  point without Python-side command-line parsing.

## Project Structure

The project has three cooperating layers. The Python packaging layer exposes the public
API and locates the bundled runtime. The Java execution layer contains the Ghostwriter
processor, which performs command-line processing and returns its result. The build layer
assembles the Java runtime into the Python distribution, allowing the Python layer to
load it without additional class-path configuration.

## Installation

Install the Python package in an environment with Python 3.9 or newer, JPype1, and a
compatible Java runtime. Define `JAVA_HOME` to point to the JDK or JVM installation
before using the wrapper:

```bash
set JAVA_HOME=C:\\Path\\To\\Your\\JDK
python -m pip install .
```

The package declares `jpype1>=1.4.0` as a dependency. A JVM must be discoverable through
`jpype.getDefaultJVMPath()`, and the bundled Ghostwriter archive must be present in the
installed package's `jars` resource directory.

## Usage

Call `gw` with the same argument sequence you would pass to the Ghostwriter CLI:

```python
from machai.gw.ghostwriter import gw

result = gw(["--help"])
print(result)
```

The JVM starts on the first call and is reused by later calls. The wrapper can also be
invoked as a module:

```bash
python -m machai.gw.ghostwriter --help
```

## Building

Build the distributable Java archive with Maven from the project root:

```bash
mvn clean package
```

The assembly configuration places the resulting runtime archive in the Python package's
`jars` directory. The Maven project depends on the Machai `ghostwriter` and
`bindex-core` components at the version declared by the parent project.

## Requirements

- **Python 3.9 or newer** — the wrapper uses the built-in generic list annotation syntax
  (`list[str]`).
- **JPype1** (`jpype1>=1.4.0`).
- **A supported Java runtime** — define `JAVA_HOME` and ensure a JVM is accessible
  through `jpype.getDefaultJVMPath()`.

## License

Refer to the repository's project metadata for licensing information.
