<!-- @guidance: >>> ${guidances}/readme-content.md 
This is a python wraper of ghostwriter cli.

- Analyze `machai.gw` python package and detailed describe it in this readme file.
- no maven-central shields required.
-->

# Ghostwriter Python Wrapper (`gw-python`)

`gw-python` is a Python wrapper around the Machai **Ghostwriter** command-line
processor. It packages the Ghostwriter Java application and exposes it through the
`machai.gw` Python package, using [JPype](https://jpype.readthedocs.io/) to start an
embedded JVM and invoke the Java implementation directly from Python.

## Introduction

The wrapper keeps the Java runtime artifact (`ghostwriter.jar`) next to the Python
package and resolves it relative to the package installation directory. This means the
consumer does not need to configure a class path manually — the wrapper discovers the
bundled archive on its own.

The public entry point is the `gw` function. It accepts a list of command-line
arguments, starts the JVM lazily on first use, invokes
`org.machanism.machai.gw.processor.Ghostwriter.main`, prints the returned result, and
returns it to the caller.

## The `machai.gw` Package

The Python package is organized as follows:

```
machai.gw/
└── machai/
    └── gw/
        ├── __init__.py          # Package marker (empty)
        ├── gw.py                # Public wrapper API and JVM bootstrapping
        └── jars/
            └── ghostwriter.jar  # Bundled Ghostwriter Java runtime artifact
```

### `machai.gw.gw` module

The module exposes two functions and resolves the bundled JAR at import time:

| Symbol | Kind | Description |
| --- | --- | --- |
| `BASE_DIR` | Module constant | Absolute path to the directory containing `gw.py`, computed from `__file__`. |
| `JAR_PATH` | Module constant | Absolute path to `jars/ghostwriter.jar`, resolved relative to `BASE_DIR`. |
| `ensure_jvm()` | Function | Starts the JVM via JPype if it is not already running. The bundled `ghostwriter.jar` is placed on the JVM class path and `convertStrings=True` is enabled so Java strings are transparently converted to Python `str`. Calling it repeatedly is safe — it is a no-op once the JVM is started. |
| `gw(args: list[str]) -> str` | Function | The primary API. It first calls `ensure_jvm()`, imports the Java class `org.machanism.machai.gw.processor.Ghostwriter`, calls its static `main(args)` method with the supplied argument list, prints the result, and returns it. |

The module is also runnable as a script. When executed directly
(`python -m machai.gw.gw ...`), it forwards `sys.argv[1:]` to `gw()`, mirroring the
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

The project is composed of three cooperating layers:

- **Python integration layer** — `machai.gw.gw` locates the packaged Java archive,
  starts JPype with that archive on the JVM class path, and forwards arguments to
  Ghostwriter.
- **Java execution layer** — the bundled Ghostwriter processor
  (`org.machanism.machai.gw.processor.Ghostwriter`) performs the command-line work and
  returns its result to the Python caller.
- **Build and packaging layer** — Maven assembles the Ghostwriter Java runtime artifact
  directly into the Python package (`machai/gw/jars/ghostwriter.jar`) so the wrapper can
  locate it without any additional configuration.

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
from machai.gw.gw import gw

result = gw(["--help"])
print(result)
```

The JVM is started only on the first call; later calls reuse it. The wrapper can also be
invoked as a module script:

```bash
python -m machai.gw.gw --help
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
