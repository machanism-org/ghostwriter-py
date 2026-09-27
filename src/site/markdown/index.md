<!-- @guidance: >>> ${guidances}/index-content.md 
This is a python wraper of ghostwriter cli.

- Add [![PyPI Version](https://img.shields.io/pypi/v/mgw)](https://pypi.org/project/mgw/)
- Add [![Test PyPI Version](https://img.shields.io/pypi/v/mgw?pypiBaseUrl=https://test.pypi.org&style=flat&label=test.pypi)](https://test.pypi.org/project/mgw/)
- Analyze `src/main/python` python project and detailed describe it in this readme file.
- Each public method should be described with a detailed API. Use multi-line snippet style to show the method signature if it is long.
- no maven-central shields required.
- do not show project site url.
- JAVA_HOME should be defined.
--> 

# Machai Ghostwriter Python Wrapper (`mgw`)

[![PyPI Version](https://img.shields.io/pypi/v/mgw)](https://pypi.org/project/mgw/) [![Test PyPI Version](https://img.shields.io/pypi/v/mgw?pypiBaseUrl=https://test.pypi.org&style=flat&label=test.pypi)](https://test.pypi.org/project/mgw/)

`mgw` packages a Python interface around the Machai Ghostwriter Java command-line processor. It provides a direct Python API, an installed `mgw` console command, and the `python -m mgw` entry point. The Java runtime is bundled with the package and launched lazily through JPype, so users do not need to manage a Java class path manually.

## Introduction

The wrapper solves the integration problem of using Ghostwriter from Python applications, Python automation, and shell scripts while retaining the Java processor's capabilities. The `gw` entry point forwards Ghostwriter command-line arguments, `gdp` exposes direct guidance-document processing, and `adw` executes an Act against a project. Results are converted to convenient Python values: `gw` returns the Java result string, while `gdp` and `adw` return Python lists.

At runtime, the package locates its bundled Ghostwriter JAR relative to the installed `mgw` package. On the first operation it validates `JAVA_HOME`, discovers a usable JVM through JPype, starts it with the bundled runtime, and reuses that JVM for subsequent calls. Optional local JARs and Maven coordinates can be supplied to the direct processor APIs and are resolved before JVM startup. The implementation uses Python 3.10 union-type syntax; install it with Python 3.10 or newer. Runtime dependencies are `jpype1` and `jgo`.

The package initializer exports `gw`, `gdp`, and `adw` lazily. The implementation module contains the JVM lifecycle, library resolution, command forwarding, guidance processing, and Act processing logic. Packaging metadata exposes the `mgw` console script, while the Maven release build assembles the Java runtime into the Python distribution.

## Project Structure

The project is organized as a small bridge between Python callers and the Ghostwriter processor. The public API layer lazily exports `gw`, `gdp`, and `adw`; the entry-point layer supports both the installed console command and `python -m mgw`; and the wrapper layer accepts command-line or structured calls. The JVM bridge validates the Java environment, resolves optional libraries, and starts JPype only when an operation is first requested. The bundled runtime supplies the Ghostwriter implementation, which performs the requested command, guidance, or Act operation and returns results to Python. The build and packaging configuration places that runtime beside the Python package so installation remains self-contained, while the external Python and Java runtimes provide execution services.

![C4 Project Diagram](./images/c4-diagram.png)

## Installation and Prerequisites

Use Python 3.10 or newer, install the package with `pip`, and use a Java installation supported by JPype. The implementation uses modern type-union syntax, so Python 3.10+ is required even though the packaging metadata currently declares `>=3.9`. `JAVA_HOME` **must be defined** and must point to an existing JDK or JVM installation before the first API or CLI invocation.

On Windows PowerShell:

```powershell
$env:JAVA_HOME = "C:\Path\To\Your\JDK"
$env:Path = "$env:JAVA_HOME\bin;$env:Path"
python -m pip install mgw
```

For a local checkout, build the Java runtime and install the Python project:

```powershell
mvn clean package -Prelease
python -m pip install .\src\main\python
```

The package installs `jpype1>=1.4.0` and `jgo>=1.0.0` automatically. JPype must be able to locate a valid JVM library through the configured Java installation.

## Usage

### Console and module entry points

Both command-line forms forward arguments to Ghostwriter:

```powershell
mgw --help
python -m mgw --help
```

### Command API

Use `gw(args)` when an application needs the normal Ghostwriter command interface. `args` is an optional list of command-line argument strings. If omitted, the function forwards the current process arguments after the executable name. It returns the result from `Ghostwriter.main` as a string.

```python
from mgw import gw

result = gw(["--help"])
print(result)
```

The JVM is started only when `gw` is first called. A later call reuses the already-started JVM; JPype does not support restarting a JVM after shutdown.

### Guidance processing API

`gdp` scans project documents for guidance tags and returns the processor report as a Python list. Its signature is:

```python
gdp(
    model=None,
    project_dir=None,
    path=".",
    config_file="gw.properties",
    instructions=None,
    threads=None,
    excludes=None,
    non_recursive=False,
    module_thread_timeout_minutes=None,
    libs=None,
)
```

It constructs a `GuidanceProcessor`, applies the optional processor settings, scans the requested project-relative path, and converts the Java report to a native list.

- `model` optionally selects the provider/model configuration.
- `project_dir` identifies the project root; the current directory is used when omitted.
- `path` is passed to the Java processor as a relative path, glob, or regular-expression matcher.
- `config_file` selects the properties configurator, and `instructions` supplies optional processing instructions.
- `threads`, `excludes`, `non_recursive`, and `module_thread_timeout_minutes` control traversal and processing. Thread and timeout values must be positive integers; a string or bytes value is not valid for `excludes`.
- `libs` is an optional list-like collection of existing library paths or Maven coordinates. Coordinates in `groupId:artifactId:version` or four-part form are resolved with `jgo`.
- `libs` must not be a string or bytes value; each entry must be a non-empty string naming a local path or resolvable Maven coordinate. Invalid thread and timeout values raise `ValueError`; invalid `libs` containers raise `TypeError`, invalid entries raise `ValueError`, and unresolved libraries raise `FileNotFoundError` before processing.

```python
from mgw.ghostwriter import gdp

report = gdp(path="src", project_dir=".", threads=2)
for item in report:
    print(item)
```

### Act processing API

`adw` executes a named Act or Act expression and returns its results as a Python list. Its signature is:

```python
adw(
    act,
    model=None,
    project_dir=None,
    path=".",
    config_file="gw.properties",
    acts_location=None,
    interactive=False,
    disable_normal_order=False,
    libs=None,
)
```

`act` must be a non-empty string. The remaining options select the model, project and configuration, Act location, interactive behavior, normal ordering, and optional libraries. The Java result collection is explicitly converted to a native list.

Parameters are interpreted as follows:

- `act` is the required Act name or expression; an empty or non-string value
  raises `ValueError`.
- `model` optionally selects the provider/model, and `project_dir` selects the
  project root (the current directory is the default).
- `path` identifies the project-relative path, glob, or regular-expression
  matcher to scan. `config_file` names the properties configurator file.
- `acts_location` optionally selects where Acts are loaded from.
- `interactive` enables interactive Act processing, while
  `disable_normal_order` disables the processor's normal ordering behavior.
- `libs` is an optional list-like collection of existing library paths or
  resolvable Maven coordinates. It cannot be a string or bytes value; a
  non-string or empty entry raises `ValueError`, and an unresolved library
  raises `FileNotFoundError` before processing.

```python
from mgw import adw

results = adw("my-act", project_dir=".", path="src")
for result in results:
    print(result)
```

### Library resolution and errors

For `gdp` and `adw`, `libs` can combine local JAR paths and Maven coordinates:

```python
report = gdp(
    path="src",
    libs=["com.example:example-library:1.0.0", "lib/custom-tools.jar"],
)
```

The wrapper rejects invalid argument types and values before processing. If `JAVA_HOME` is missing, does not name a directory, or does not lead to a discoverable JVM, it reports the problem on standard error and exits with status 1. Library resolution failures are reported as file-not-found errors.

## API Summary

| Public API | Purpose | Return value |
| --- | --- | --- |
| `mgw.gw(args=None)` | Forward Ghostwriter command-line arguments through the bundled Java runtime; omitted `args` means the current process arguments after the executable name. | `str` |
| `mgw.gdp(...)` | Lazily exposed package-level form of the guidance processor API. | `list` |
| `mgw.adw(act, ...)` | Lazily exposed package-level form of the Act processor API. | `list` |
| `mgw.ghostwriter.gdp(...)` | Scan documents, configure guidance processing, and return the report. | `list` |
| `mgw.ghostwriter.adw(act, ...)` | Configure and execute an Act against a project. | `list` |
| `mgw.ghostwriter.gw(args=None)` | Direct-module form of the command API. | `str` |

The package also defines the public module hook `mgw.__getattr__(name)`. Its
signature is:

```python
__getattr__(name: str)
```

It returns `gw`, `gdp`, or `adw` when one of those names is requested and
raises `AttributeError` for unknown names. This lazy resolution keeps imports
light and avoids eager JVM-related imports. The implementation's private
`_resolve_library(value)` accepts an existing path or a three- or four-part
Maven coordinate, and `_ensure_jvm_started(libs=None)` validates `JAVA_HOME`,
resolves optional libraries, and starts or reuses JPype's JVM; these helpers
are intentionally private and are not part of the public API.

## Building and Releasing

From the project root, assemble the Java runtime and build the Python artifacts:

```powershell
mvn clean package -Prelease
Set-Location src/main/python
python -m pip install --upgrade build
python -m build
```

The wheel and source distribution are written to the Python project's `dist` directory. The release profile assembles the Java runtime, and Hatchling includes that runtime in the Python wheel.

## License

Apache License, Version 2.0.
