<!-- @guidance: >>> ${guidances}/readme-content.md -->

# Ghostwriter Python Wrapper (`gw-python`)

[![Maven Central](https://img.shields.io/maven-central/v/org.machanism.machai/ghostwriter-py.svg)](https://central.sonatype.com/artifact/org.machanism.machai/ghostwriter-py)

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

`gw-python` is a Python wrapper around the Machai **Ghostwriter** command-line
processor. It packages the Ghostwriter Java application and exposes it through the
`machai.gw` Python package, using [JPype](https://jpype.readthedocs.io/) to start an
embedded JVM and invoke the Java implementation directly from Python.

## Introduction

The wrapper keeps the Ghostwriter runtime archive next to the Python package and resolves
its absolute path from the installed package location. Consumers therefore do not need to
configure a Java class path manually. The public `gw` function accepts a list of
command-line arguments, starts the JVM lazily on first use, invokes
`org.machanism.machai.gw.processor.Ghostwriter.main`, and returns the Java result as a
Python string.

The Java implementation remains responsible for Ghostwriter's command-line behavior;
the Python layer provides packaging, JVM startup, and argument forwarding rather than
reimplementing that behavior. The public entry point is the `gw` function in
`machai.gw.ghostwriter`.

## The `machai.gw` Package

The Python package is organized as follows:

```
machai.gw/
└── machai/
    └── gw/
        ├── __init__.py          # Package marker (empty)
        ├── ghostwriter.py       # Public wrapper API and JVM bootstrapping
        └── jars/
            └── ghostwriter.jar  # Bundled Ghostwriter Java runtime artifact
```

### `machai.gw.ghostwriter` module

The module exposes the wrapper function and resolves the bundled JAR at import time:

| Symbol | Kind | Description |
| --- | --- | --- |
| `BASE_DIR` | Module constant | Absolute path to the directory containing `ghostwriter.py`, computed from `__file__`. |
| `JAR_PATH` | Module constant | Absolute path to `jars/ghostwriter.jar`, resolved relative to `BASE_DIR`. |
| `gw(args: list[str]) -> str` | Function | The primary API. It starts JPype if needed, places the bundled archive on the JVM class path with `convertStrings=True`, imports `org.machanism.machai.gw.processor.Ghostwriter`, invokes its static `main(args)` method, and returns the result. |

The module is also runnable as a script. When executed directly
(`python -m machai.gw.ghostwriter ...`), it forwards `sys.argv[1:]` to `gw()`, mirroring the
behavior of the underlying Ghostwriter CLI.

### Design notes

- **Lazy JVM startup.** The JVM is created only on the first call to `gw()` (through
  `ensure_jvm()`). Because JPype does not support restarting a JVM after shutdown within
  the same process, all subsequent calls reuse the already-running JVM.
- **Self-contained artifact resolution.** `JAR_PATH` is derived from the package
  location, so the wrapper works regardless of the current working directory or how the
  package is installed.
- **Transparent type conversion.** `convertStrings=True` ensures the Java `String`
  result of `Ghostwriter.main` is returned to Python as a native `str`.

## Project Structure

The project has three cooperating layers. The Python packaging layer exposes the public
API and locates the bundled runtime. The Java execution layer contains the Ghostwriter
processor, which performs command-line processing and returns its result. The build layer
assembles the Java runtime into the Python distribution, allowing the Python layer to
load it without additional class-path configuration.

## Installation

Install the Python package into an environment that has Python 3.9 or newer and a
compatible Java runtime:

```bash
python -m pip install .
```

The package declares `jpype1>=1.4.0` as a dependency. The Ghostwriter archive must be
available at `machai/gw/jars/ghostwriter.jar` inside the installed package, and a Java
runtime must be discoverable through `jpype.getDefaultJVMPath()`.

## Usage

Use the `gw` function with the same argument sequence you would pass to the Ghostwriter
CLI:

```python
from machai.gw.ghostwriter import gw

result = gw(["--help"])
print(result)
```

The JVM is started only on the first call; later calls reuse it. The wrapper can also be
invoked as a module script:

```bash
python -m machai.gw.ghostwriter --help
```

## Building

Build the distributable Java archive with Maven from the project root:

```bash
mvn clean package
```

The assembly configuration places the resulting `ghostwriter.jar` into the Python
package's `jars` directory. The Maven project (`gw-python`) depends on the Machai
`ghostwriter` and `bindex-core` components at the version declared by the parent
project.

## Requirements

- **Python 3.9 or newer** — the wrapper uses the built-in generic list annotation syntax
  (`list[str]`).
- **JPype1** (`jpype1>=1.4.0`).
- **A supported Java runtime** — a JVM accessible through
  `jpype.getDefaultJVMPath()`.

## License

Refer to the repository's project metadata for licensing information.
