<!-- @guidance: >>> ${guidances}/readme-content.md
- no img.shields.io/maven-central required.
- Add link to the project site: https://machai.machanism.org/ghostwriter-py/
-->

# Ghostwriter Python Wrapper (`mgw`)

`mgw` is a Python wrapper around the Machai Ghostwriter command-line processor.
It packages the Ghostwriter Java runtime and uses JPype to start an embedded JVM,
forward command-line arguments, and return the Java processor's result.

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

Project site: [Machai Ghostwriter Python project site](https://machai.machanism.org/ghostwriter-py/)

## Introduction

The Python project under `src/main/python` contains the `mgw` package and its
Hatch build configuration. It targets Python 3.9 or newer, declares
`jpype1>=1.4.0`, and provides the `mgw` console entry point. The wheel includes
`mgw/jars/ghostwriter.jar`, produced by the Maven build, as the Java runtime
used by the wrapper.

The `mgw.__main__.gw` function accepts an optional `list[str]`. With no list, it
forwards the process arguments after the executable name. On its first
invocation it resolves the bundled runtime relative to the installed package,
starts JPype with string conversion enabled, and invokes
`org.machanism.machai.gw.processor.Ghostwriter.main`. Later calls reuse the
running JVM; JPype does not support restarting a JVM after shutdown.

The package initializer is intended to expose `gw` lazily, while the module
entry point provides JVM startup and argument forwarding. The installed console
script calls `mgw.__main__.gw` directly.

## The `mgw` Package

The Python distribution contains the `mgw` package and the bundled runtime JAR
in its `jars` resource directory.

| Symbol | Kind | Description |
| --- | --- | --- |
| `mgw.__main__.gw(args: list[str] | None = None) -> str` | Function | Starts JPype if necessary, places the bundled archive on the JVM class path, invokes the Java processor, and returns its result. With no argument, it forwards `sys.argv[1:]`. |
| `mgw.__main__.BASE_DIR` | Module constant | Absolute path to the directory containing the installed Python package. |
| `mgw.__main__.JAR_PATH` | Module constant | Absolute path to the bundled `jars/ghostwriter.jar`, resolved relative to `BASE_DIR`. |

### Runtime behavior

- **Lazy JVM startup.** The JVM is created only when `gw()` is first called and
  later calls reuse it.
- **Self-contained artifact resolution.** The archive path is derived from the
  installed package location, independent of the current working directory.
- **Transparent string conversion.** JPype is started with `convertStrings=True`,
  making the Java result available as a native Python `str`.
- **Direct argument forwarding.** The supplied argument list is passed to the
  Java entry point without Python-side command-line parsing.

## Project Structure

The project has three cooperating layers. The Python packaging layer installs
the `mgw` console entry point and locates the bundled runtime. The Java execution
layer contains the Ghostwriter processor, which performs command-line processing
and returns its result. The Maven build layer assembles the Java runtime into the
Python distribution, allowing the Python layer to load it without additional
class-path configuration. No diagram image is included because the repository
does not contain the referenced visual resource.

## Installation

Install the Python package in an environment with Python 3.9 or newer, JPype1,
and a compatible Java runtime. **`JAVA_HOME` must be defined** and should point
to the JDK or JVM installation before using the wrapper:

```powershell
$env:JAVA_HOME = "C:\Path\To\Your\JDK"
python -m pip install .
```

The package declares `jpype1>=1.4.0` as a dependency. A JVM must be discoverable
through `jpype.getDefaultJVMPath()`, and the bundled Ghostwriter archive must be
present in the installed package's `jars` resource directory.

## Usage

Import `gw` from the module entry point and pass the same argument sequence you
would pass to the Ghostwriter CLI:

```python
from mgw.__main__ import gw

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

Arguments are forwarded directly to Ghostwriter without Python-side command-line
parsing. The JVM starts on the first call and is reused by later calls in the
same process.

## Building

Build the distributable Java runtime archive with Maven from the project root:

```bash
mvn clean package
```

Then build the Python source distribution and wheel from `src/main/python`:

```bash
python -m pip install --upgrade build
cd src/main/python
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
- **A supported Java runtime** with **`JAVA_HOME` defined** and accessible through
  `jpype.getDefaultJVMPath()`.
- **The Ghostwriter runtime archive**, included with the installed package.

## License

Refer to the repository's project metadata for licensing information.
