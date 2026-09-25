<!-- @guidance: >>> ${guidances}/readme-content.md 
This is a python wraper of ghostwriter cli.

- Analyze `machai.gw` python package and detailed describe it in this readme file.
- no maven-central shields required.
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

`gw-python` is a Python wrapper around the Machai **Ghostwriter** command-line
processor. It packages the Ghostwriter Java application and exposes it through the
`machai.gw` Python package, using [JPype](https://jpype.readthedocs.io/) to start an
embedded JVM and invoke the Java implementation directly from Python.

## Introduction

The wrapper keeps the Java runtime artifact (`ghostwriter.jar`) next to the Python
package and resolves it relative to the package installation directory. This means the
consumer does not need to configure a class path manually — the wrapper discovers the
bundled archive on its own.

The public entry point is the `gw` function in `machai.gw.ghostwriter`. It accepts a
list of command-line arguments, starts the JVM lazily on first use, invokes
`org.machanism.machai.gw.processor.Ghostwriter.main`, prints the returned result, and
returns it to the caller.

## The `machai.gw` Package

The Python package is organized as follows:

```
machai.gw/
└── machai/
    └── gw/
        ├── __init__.py          # Package marker
        ├── ghostwriter.py       # Public wrapper API and JVM bootstrapping
        └── jars/
            └── ghostwriter.jar  # Bundled Ghostwriter Java runtime artifact
```

### `machai.gw.ghostwriter` module

The module exposes two functions and resolves the bundled JAR at import time:

| Symbol | Kind | Description |
| --- | --- | --- |
| `BASE_DIR` | Module constant | Absolute path to the directory containing `ghostwriter.py`, computed from `__file__`. |
| `JAR_PATH` | Module constant | Absolute path to `jars/ghostwriter.jar`, resolved relative to `BASE_DIR`. |
| `ensure_jvm()` | Function | Starts the JVM via JPype if it is not already running. The bundled `ghostwriter.jar` is placed on the JVM class path and `convertStrings=True` is enabled so Java strings are transparently converted to Python `str`. Calling it repeatedly is safe — it is a no-op once the JVM is started. |
| `gw(args: list[str]) -> str` | Function | The primary API. It first calls `ensure_jvm()`, imports the Java class `org.machanism.machai.gw.processor.Ghostwriter`, calls its static `main(args)` method with the supplied argument list, prints the result, and returns it. |

The module is also runnable as a script. When executed directly
(`python -m machai.gw.ghostwriter ...`), it forwards `sys.argv[1:]` to `gw()`,
mirroring the behavior of the underlying Ghostwriter CLI.

### Design notes

- **Lazy JVM startup.** The JVM is created only on the first call to `gw()` (through
  `ensure_jvm()`). Because JPype does not support restarting a JVM after shutdown within
  the same process, all subsequent calls reuse the already-running JVM.
- **Self-contained artifact resolution.** `JAR_PATH` is derived from the package
  location, so the wrapper works regardless of the current working directory or how the
  package is installed.
- **Transparent type conversion.** `convertStrings=True` ensures the Java `String`
  result of `Ghostwriter.main` is returned to Python as a native `str`.
- **Argument forwarding.** The wrapper passes the caller's argument list directly to the
  Java entry point, preserving the command-line interface rather than reimplementing its
  parsing in Python.

## Project Structure

The project has three cooperating layers. The Python package provides the public API and
locates the bundled Java runtime. The Java execution layer contains the Ghostwriter
processor that performs the command-line work and returns its result. The build and
packaging layer assembles that runtime into the Python distribution, allowing the Python
layer to find it without additional class-path configuration.

## Installation

Install the Python package into an environment that has a compatible Java runtime and
JPype available:

```bash
python -m pip install jpype1
python -m pip install .
```

The package expects the Ghostwriter archive to be available at
`machai/gw/jars/ghostwriter.jar` inside the installed package. A Java runtime must
therefore be installed and discoverable through `jpype.getDefaultJVMPath()`.

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
package's `jars` directory. The Maven project (`ghostwriter-py`) depends on the Machai
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
