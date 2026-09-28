<!-- @guidance: >>> ${guidances}/readme-content.md
- Add ![PyPI Version](https://img.shields.io/pypi/v/mgw)
- Add ![Test PyPI Version](https://img.shields.io/pypi/v/mgw?pypiBaseUrl=https://test.pypi.org&style=flat&label=test.pypi)
- Add link to the project site: https://machai.machanism.org/ghostwriter-py/
-->

# Machai Ghostwriter Python Wrapper (`mgw`)

[![PyPI Version](https://img.shields.io/pypi/v/mgw)](https://pypi.org/project/mgw/) [![Test PyPI Version](https://img.shields.io/pypi/v/mgw?pypiBaseUrl=https://test.pypi.org&style=flat&label=test.pypi)](https://test.pypi.org/project/mgw/)

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

`mgw` is a Python wrapper for the Machai Ghostwriter command-line processor. It provides a Python API, an installed console command, and a module entry point while packaging the Java Ghostwriter runtime alongside the Python distribution. The wrapper locates the bundled runtime relative to the installed package and uses JPype to invoke it, so callers do not need to configure a Java class path manually.

Project site: <https://machai.machanism.org/ghostwriter-py/>

## Introduction

The project bridges a Python packaging and command-line experience with the Ghostwriter Java implementation. It lets Python applications and shell users invoke Ghostwriter with the same argument sequence while keeping the Java runtime self-contained in the installed package. The wrapper exposes `gw` for command-line processing, `gdp` for guidance processing, and `adw` for executing a named Act; these operations validate `JAVA_HOME`, start JPype lazily, and return the Java processor's result as a string or Python list as appropriate.

The Python package targets Python 3.9 or newer and depends on `jpype1>=1.4.0`. Its public `gw` function accepts an optional `list[str]`; when no list is provided, it forwards the current process arguments after the executable name. On first use, the wrapper discovers the JVM, starts it with string conversion enabled, adds the bundled Ghostwriter runtime to the class path, and invokes `org.machanism.machai.gw.processor.Ghostwriter.main`. Subsequent calls reuse the same JVM because JPype does not support restarting a JVM after shutdown.

The package initializer exposes the public functions lazily, while the module implementation handles argument forwarding, JVM startup, runtime resolution, and result handling. The direct processors also support optional local libraries or Maven coordinates through `jgo`. The Maven build assembles the Java runtime into the Python package, and Hatchling builds the Python source distribution and wheel with that runtime included.

## Project Structure

The project consists of four cooperating layers:

- The **public interface layer** provides lazy Python exports and the console and module entry points.
- The **JVM bridge layer** validates the Java environment, resolves the packaged runtime, starts JPype, and forwards requests.
- The **processor API layer** maps Python arguments to command, guidance, and Act processors, including traversal, exclusions, thread, timeout, and optional library settings.
- The **build and packaging layer** assembles the Java runtime and includes it in the Python distribution, allowing users to install one package rather than manage a separate class path.

The Python API delegates lazily to the JVM bridge. The bridge starts the Java runtime through JPype, adds the bundled Ghostwriter runtime to the class path, and forwards arguments or structured processing options to the corresponding Java processor. CLI users can reach the same bridge through either the installed command or the Python module.

## Installation and Prerequisites

Use Python 3.9 or newer, a Java installation supported by JPype, and a working Python package installer. `JAVA_HOME` must be defined before running the wrapper and should point to a JDK or JVM installation. On Windows PowerShell, for example:

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

The package declares `jpype1>=1.4.0` and `jgo>=1.0.0` as dependencies. JPype must be able to discover the JVM at `jpype.getDefaultJVMPath()`, and the installed package must contain the bundled Ghostwriter runtime.

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
from mgw import gw

result = gw(["--help"])
print(result)
```

Arguments are forwarded without Python-side command-line parsing. The JVM starts lazily on the first call and is reused by later calls in the same process. The function returns the result produced by the Java processor as a Python string.

For direct guidance processing, use `gdp` with an optional project directory and path:

```python
from mgw import gdp

report = gdp(path="src", project_dir=".", threads=2)
for item in report:
    print(item)
```

To execute an Act, use `adw` with a non-empty Act name or expression:

```python
from mgw import adw

results = adw("my-act", path="src", project_dir=".")
```

Both functions return Python lists. Their optional settings include the model, configuration file, path matcher, Act location, interactive mode, exclusions, thread count, non-recursive traversal, module timeout, and additional libraries; these are forwarded to the corresponding Java processor after JVM startup. Thread and module-timeout values must be positive integers when supplied, exclusions and libraries must be lists, and `non_recursive` controls traversal depth.

## Python API Reference

### `gw`

```python
def gw(args: list[str] | None = None) -> str:
```

Runs the Ghostwriter Java command-line processor. `args` is an optional list of command-line arguments; when omitted, the function forwards the current process arguments after the executable name. The JVM starts lazily on the first call, and the Java result is returned as a Python string. `JAVA_HOME` must be defined before the first invocation.

### `gdp`

```python
def gdp(
    model: str | None = None,
    project_dir: str | None = None,
    path: str = ".",
    config_file: str = "gw.properties",
    instructions: str | None = None,
    threads: int | None = None,
    excludes: list[str] | None = None,
    non_recursive: bool = False,
    module_thread_timeout_minutes: int | None = None,
    libs: list[str] | None = None,
) -> list[str]:
```

Processes guidance tags in the selected project and returns the processor report as a Python list. `model` selects the provider or model, `project_dir` identifies the project, `path` selects a relative path or matcher, and `config_file` supplies the properties configuration. `instructions` overrides processor instructions; `threads`, `excludes`, `non_recursive`, and `module_thread_timeout_minutes` control concurrency and traversal. `libs` accepts local library paths or Maven coordinates. Thread and timeout values must be positive integers, while `libs` and `excludes` must be lists rather than strings.

### `adw`

```python
def adw(
    act: str,
    model: str | None = None,
    project_dir: str | None = None,
    path: str = ".",
    config_file: str = "gw.properties",
    acts_location: str | None = None,
    interactive: bool = False,
    disable_normal_order: bool = False,
    libs: list[str] | None = None,
) -> list[str]:
```

Executes a non-empty Act name or expression and returns the results as a Python list. `model`, `project_dir`, `path`, `config_file`, and `libs` have the same roles as in `gdp`; `acts_location` selects where Acts are loaded from, `interactive` enables interactive processing, and `disable_normal_order` disables the normal Act order. `JAVA_HOME` must be defined before invocation.

## Building

From the project root, assemble the Java runtime and build the Python artifacts:

```powershell
mvn clean package -Prelease
Set-Location src/main/python
python -m pip install --upgrade build
python -m build
```

The generated source distribution and wheel are placed in the Python project's `dist` directory. The Maven release profile assembles the Java runtime, and the Python wheel configuration includes it with the package.

## Requirements

- Python 3.9 or newer.
- `jpype1>=1.4.0` and `jgo>=1.0.0`.
- A supported Java runtime with `JAVA_HOME` defined.
- The bundled Ghostwriter runtime, included in the installed package.

## License

Apache License, Version 2.0.
