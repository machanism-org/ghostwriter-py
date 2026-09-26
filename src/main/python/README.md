<!-- @guidance: >>> ${guidances}/readme-content.md
- no img.shields.io/maven-central required.
- Add link to the project site: https://machai.machanism.org/ghostwriter-py/
-->

# Ghostwriter Python Wrapper (`gw-python`)

Project site: [machai.machanism.org/ghostwriter-py](https://machai.machanism.org/ghostwriter-py/)

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

`ghostwriter-py` is a Python wrapper around the Machai Ghostwriter command-line
processor. It packages the Ghostwriter Java runtime and exposes it through the
`mgw` Python package, using JPype to start an embedded JVM and invoke the Java
implementation.

## Introduction

The wrapper keeps the Ghostwriter runtime archive next to the Python package and
resolves its absolute path from the installed package location. Consumers do not
need to configure a Java class path manually. The public `gw` function accepts a
list of command-line arguments, starts the JVM lazily on first use, invokes
`org.machanism.machai.gw.processor.Ghostwriter.main`, and returns the Java result
as a Python string.

The Java implementation remains responsible for Ghostwriter's command-line
behavior. The Python layer provides packaging, JVM startup, and argument
forwarding rather than reimplementing that behavior.

## The `mgw` Package

The Python distribution contains the `mgw` package and the bundled runtime JAR in
its `jars` resource directory. The package provides the following entry points:

| Symbol | Kind | Description |
| --- | --- | --- |
| `mgw.gw` | Lazily exported function | Re-exports the wrapper function for convenient imports such as `from mgw import gw`. |
| `mgw.__main__.gw(args: list[str] | None = None) -> str` | Function | Starts JPype if necessary, places the bundled archive on the JVM class path, invokes the static Java `main(args)` method, and returns its result. With no argument, it forwards `sys.argv[1:]`. |
| `mgw.__main__.BASE_DIR` | Module constant | Absolute path to the directory containing the installed Python package. |
| `mgw.__main__.JAR_PATH` | Module constant | Absolute path to the bundled `jars/ghostwriter.jar`, resolved relative to `BASE_DIR`. |

### Runtime behavior

- **Lazy JVM startup.** The JVM is created only when `gw()` is first called. Later
  calls reuse the running JVM. JPype does not support restarting a JVM after it
  has been shut down in the same process.
- **Self-contained artifact resolution.** The archive path is derived from the
  installed package location, so the current working directory does not affect
  discovery.
- **Transparent string conversion.** JPype is started with
  `convertStrings=True`, making the Java result available as a native Python
  `str`.
- **Direct argument forwarding.** The supplied argument list is passed to the
  Java entry point without Python-side command-line parsing.

## Project Structure

The project has three cooperating layers. The Python packaging layer exposes the
public API, installs the console entry point, and locates the bundled runtime.
The Java execution layer contains the Ghostwriter processor, which performs
command-line processing and returns its result. The Maven build layer assembles
the Java runtime into the Python distribution, allowing the Python layer to load
it without additional class-path configuration. No diagram image is included
because the repository does not contain the referenced visual resource.

## Installation

Install the Python package in an environment with Python 3.9 or newer, JPype1,
and a compatible Java runtime. Define `JAVA_HOME` to point to the JDK or JVM
installation before using the wrapper:

```powershell
$env:JAVA_HOME = "C:\Path\To\Your\JDK"
python -m pip install .
```

The package declares `jpype1>=1.4.0` as a dependency. A JVM must be discoverable
through `jpype.getDefaultJVMPath()`, and the bundled Ghostwriter archive must be
present in the installed package's `jars` resource directory.

## Usage

Import `gw` from the package and pass the same argument sequence you would pass to
the Ghostwriter CLI:

```python
from mgw import gw

result = gw(["--help"])
print(result)
```

The wrapper can also be invoked through the installed command:

```bash
mgw --help
```

Or run the package as a module:

```bash
python -m mgw --help
```

The JVM starts on the first call and is reused by later calls.

## Building

Build the distributable Java runtime archive with Maven from the project root:

```bash
mvn clean package
```

Then build the Python source distribution and wheel:

```bash
python -m pip install --upgrade build
python -m build
```

The Maven assembly configuration places the runtime archive in the Python
package's `jars` directory, and the Python wheel includes that archive as a
forced resource. The Maven project depends on the Machai `ghostwriter` and
`bindex-core` components at the version declared by the parent project.

## Requirements

- **Python 3.9 or newer** — the wrapper uses the built-in generic list annotation
  syntax (`list[str]`).
- **JPype1** (`jpype1>=1.4.0`).
- **A supported Java runtime** — define `JAVA_HOME` and ensure a JVM is
  accessible through `jpype.getDefaultJVMPath()`.

## License

Refer to the repository's project metadata for licensing information.
