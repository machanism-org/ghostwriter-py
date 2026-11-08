<!-- @guidance: >>> ${guidances}/index-content.md 
This is a python wraper of ghostwriter cli.

- Add [![PyPI Version](https://img.shields.io/pypi/v/mgw)](https://pypi.org/project/mgw/)
- Add **Bindex Badge:** Include this shield *only if* `./bindex.json` exists in the repository:
    ```markdown
    [![bindex](https://img.shields.io/badge/bindex-blue.svg)](https://raw.githubusercontent.com/machanism-org/[artifactId]/refs/heads/main/bindex.json)
    ```
- Analyze `src/main/python` python project and detailed describe it in this readme file.
- Each public method should be described with a detailed API. Use multi-line snippet style to show the method signature if it is long.
- no maven-central shields required.
- do not show project site url.
- JAVA_HOME should be defined.
--> 

# Machai Ghostwriter Python Wrapper (`mgw`)

[![PyPI Version](https://img.shields.io/pypi/v/mgw)](https://pypi.org/project/mgw/) [![bindex](https://img.shields.io/badge/bindex-blue.svg)](https://raw.githubusercontent.com/machanism-org/ghostwriter-py/refs/heads/main/bindex.json)

## Introduction

`mgw` provides a Python API and command-line entry point for the Machai Ghostwriter processor. It bridges Python applications with the bundled Java implementation, allowing users to run Ghostwriter without manually assembling a Java class path. The package starts JPype lazily, validates the Java environment, loads the bundled runtime, and forwards either command-line arguments or structured guidance and Act-processing options to the appropriate Java processor.

The package includes the Ghostwriter runtime in its distribution. Its public operations cover ordinary Ghostwriter invocation (`gw`), guidance-tag processing (`gdp`), and Act execution (`adw`). Direct processor calls can also resolve additional local JAR files or Maven coordinates through `jgo`. Guidance reports and Act results are explicitly converted to Python lists; `gw` returns the Java entry point's result unchanged, with JPype string conversion enabled. Although the package metadata declares Python 3.9 or newer, the implementation evaluates union annotations using `|` at import time and therefore requires Python 3.10 or newer in practice.

## Project Structure

The system is organized around a small set of cooperating components:

- **Public API:** lazily exposes the wrapper functions so importing the package does not start a JVM.
- **Command and processor bridge:** validates `JAVA_HOME`, resolves the embedded runtime, starts JPype on first use, and maps Python arguments to Ghostwriter processors.
- **Bundled Java runtime:** supplies the Ghostwriter command, guidance processor, and Act processor used by the bridge.
- **JPype and Java runtime:** bridge Python calls into the JVM that runs the bundled processor.
- **Optional dependency resolver:** uses `jgo` to download additional Maven artifacts or accepts existing local libraries for direct processor calls.
- **CLI entry points:** accept Ghostwriter arguments from an installed command or Python module and pass them through unchanged.

The public API delegates to the bridge, which starts the Java runtime with the bundled processor on its class path. The direct processors additionally configure project traversal, models, configuration files, exclusions, concurrency, timeouts, Act locations, and optional libraries before scanning the requested project.

![C4 Project Diagram](./images/c4-diagram.png)

## Prerequisites and Installation

Before using the current implementation, install Python 3.10 or newer and a Java installation supported by JPype and the bundled Ghostwriter runtime. The Maven project targets Java 17; use a JDK 17 or newer for local builds. `JAVA_HOME` **must be defined** before JVM startup and must point to an existing JDK installation; JPype must also be able to locate a valid JVM library. The package dependencies include `jpype1>=1.4.0` and `jgo>=1.0.0`, which pip installs automatically. The declared Python minimum of 3.9 is lower than the implementation's effective minimum because its annotations are not postponed.

On Windows PowerShell, configure the Java environment and install the published package:

```powershell
$env:JAVA_HOME = "C:\Path\To\Your\JDK"
$env:Path = "$env:JAVA_HOME\bin;$env:Path"
python -m pip install mgw
```

For a local checkout, install Maven and the Python build frontend first, then build the embedded runtime and install the Python package. The release profile invokes `python -m build` during Maven's package phase:

```powershell
python -m pip install --upgrade build
mvn clean package -Prelease
python -m pip install .\src\main\python
```

The installed package contains the Java runtime, so no separate class-path configuration is required. The JVM is started only when one of the public operations is first invoked and is reused for subsequent calls in the same process. Do not shut it down between calls: JPype cannot restart a JVM in that process. If another library starts the JVM first, that library must make the Ghostwriter classes available; the wrapper does not add the bundled runtime to an already-running JVM.

## Usage

### Command line

Ghostwriter arguments can be passed directly through either supported entry point:

```powershell
mgw --help
python -m mgw --help
```

### General Ghostwriter invocation

Use `gw` when the caller already has the argument sequence expected by Ghostwriter:

```python
from mgw import gw

result = gw(["--help"])
print(result)
```

If `args` is omitted, `gw` forwards the current process arguments after the executable name. It returns the Java Ghostwriter entry point's result without an explicit Python conversion; its annotation is `str`, but a Java void result would be `None`.

### Guidance processing

Use `gdp` to scan a project for guidance tags. The path may be a relative path, glob, or regular-expression matcher understood by the Java processor:

```python
from mgw import gdp

report = gdp(path="src", project_dir=".", threads=2)
for item in report:
    print(item)
```

### Act execution

Use `adw` to execute a named Act or Act expression against a project:

```python
from mgw import adw

results = adw("my-act", path="src", project_dir=".")
for result in results:
    print(result)
```

For real guidance or Act processing, configure the provider/model and credentials required by Ghostwriter in the chosen properties configuration or its supported environment settings. Pass `model` to select a provider/model explicitly, or leave it as `None` to preserve Java-side configuration resolution. `gw(["--help"])` exposes the bundled processor's CLI options; the Python wrapper does not parse those options or define its own provider configuration syntax. Replace the illustrative Act and library names below with resources available to your project.

Additional libraries may be existing local paths or Maven coordinates (`groupId:artifactId:version`, or the four-part form accepted by `jgo`). Relative local library paths are resolved from the Python process's current working directory, not `project_dir`. Supply all required libraries on the first `gdp` or `adw` call, before any `gw` call starts the JVM:

```python
report = gdp(
    path="src",
    libs=["com.example:example-library:1.0.0", "lib/custom-tools.jar"],
)
```

## Python API Reference

### `gw`

```python
def gw(args: list[str] | None = None) -> str:
```

Runs `Ghostwriter.main(args)` through JPype without Python-side option parsing.

- **`args`:** a list of strings forwarded unchanged to Java. `None` uses `sys.argv[1:]`; an empty list supplies no arguments.
- **Return:** the Java entry point's result unchanged. The annotation is `str` and JPype converts Java strings to Python strings, but the wrapper does not enforce a string return or convert a Java void result away from `None`.
- **Side effects and failures:** starts the JVM on first use and executes the Java command, which may perform project processing according to its arguments. JVM setup failures and Java exceptions follow the shared error behavior below. There is no wrapper-side validation of CLI arguments.

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

Constructs a Java `GuidanceProcessor` with the project directory, model, and `PropertiesConfigurator`, applies the supplied settings, then calls `scanDocuments` synchronously. Guidance processing can update matching project files.

| Parameter | Default | Behavior |
| --- | --- | --- |
| `model` | `None` | Provider/model identifier; `None` leaves resolution to the Java configuration. |
| `project_dir` | `None` | Project root, converted to an absolute path; `None` uses the current working directory. |
| `path` | `"."` | Project-relative path, glob, or regular-expression matcher passed unchanged to the Java scanner. |
| `config_file` | `"gw.properties"` | Properties configuration supplied to `PropertiesConfigurator`; loading and interpretation are Java-side concerns. |
| `instructions` | `None` | When supplied, converted to a string and passed to `setInstructions`; otherwise preserves processor defaults. |
| `threads` | `None` | Positive integer concurrency limit; `None` preserves the Java default. Booleans are rejected. |
| `excludes` | `None` | List of excluded path patterns, each converted to a string; `None` leaves the Java defaults unchanged. A single string or bytes value is rejected. |
| `non_recursive` | `False` | Converted to a boolean and passed to the traversal setting; `True` requests non-recursive scanning. |
| `module_thread_timeout_minutes` | `None` | Positive integer module timeout in minutes; `None` preserves the Java default. Booleans are rejected. |
| `libs` | `None` | Additional local library paths or Maven coordinates; `None` supplies no additional libraries. A single string or bytes value is rejected. |

**Return:** `list(guidance_processor.getReport())`, annotated as `list[str]`. The container is converted explicitly; elements are not separately cast to strings. Java strings are converted by JPype when the wrapper starts the JVM.

**Validation:** invalid thread or timeout values raise `ValueError`; string/bytes `libs` or `excludes` raise `TypeError`. Except for the `libs` container check, settings validation happens after JVM startup and processor construction, so an invalid call can still start the JVM. See shared errors below for library, startup, and processor failures.

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

Constructs a Java `ActProcessor`, configures Act execution, and calls `scanDocuments` synchronously. The Java processor handles Act loading, expression syntax, episode selection, and any resulting project changes.

| Parameter | Default | Behavior |
| --- | --- | --- |
| `act` | Required | Non-empty string containing an Act name or expression. Whitespace-only strings are rejected, but valid input is forwarded without trimming. |
| `model` | `None` | Provider/model identifier; `None` preserves Java-side configuration resolution. |
| `project_dir` | `None` | Project root converted to an absolute path; `None` uses the current working directory. |
| `path` | `"."` | Project-relative path or matcher passed unchanged to the Java scanner. |
| `config_file` | `"gw.properties"` | Properties configuration passed to `PropertiesConfigurator`. |
| `acts_location` | `None` | Location from which Acts are loaded; supplied values are converted to strings. `None` preserves the Java default. |
| `interactive` | `False` | Converted to a boolean and passed to `setInteractive`; use `False` for unattended execution. |
| `disable_normal_order` | `False` | Converted to a boolean; `True` requests disabling the normal Act order. |
| `libs` | `None` | Additional local library paths or Maven coordinates, resolved as in `gdp`; a single string or bytes value is rejected. |

**Return:** `list(processor.getResults())`, annotated as `list[str]`. As with `gdp`, only the container is explicitly converted by Python.

**Validation:** a non-string, empty, or whitespace-only `act` raises `ValueError` before JVM startup. A string/bytes `libs` raises `TypeError` before startup. Library, JVM, and Java processor errors follow the shared behavior below.

### Shared JVM and error behavior

All three operations lazily load the wrapper through the package's public exports. The public API consists of `gw`, `gdp`, and `adw`; the module attribute hook is an implementation detail, not a separate processor operation.

- Missing or non-directory `JAVA_HOME`, a resolved JVM library path that does not exist, or a caught JVM startup failure prints a diagnostic to standard error and raises `SystemExit(1)`. Python applications that need to handle these cases must account for `SystemExit`, not only `Exception`.
- Exceptions raised by `jpype.getDefaultJVMPath()` itself propagate rather than being converted to `SystemExit`.
- Library entries must be non-empty strings, otherwise resolution raises `ValueError`. A nonexistent path that is not a valid three- or four-part Maven coordinate raises `FileNotFoundError`; Maven resolution failures are also wrapped in `FileNotFoundError`. Import errors for the resolver can propagate.
- Libraries are resolved before the startup environment checks. With an existing JVM, they are submitted to `jpype.addClassPath`, but this cannot reliably change an already-loaded JVM's system class path. Provide libraries before relevant Java classes are loaded, preferably on the first processor call.
- Java class-loading, configuration, scanning, and processor exceptions propagate through JPype; the wrapper does not retry or roll back project changes.

## Building

From the repository root, with Maven and JDK 17 or newer configured, install the build frontend and run the release profile to assemble the Java runtime and build the Python source distribution and wheel:

```powershell
python -m pip install --upgrade build
mvn clean package -Prelease
```

The release profile assembles `src/main/python/mgw/jars/ghostwriter.jar` and invokes `python -m build` in `src/main/python`. Hatchling is the Python build backend, and the wheel configuration explicitly includes the runtime. The source distribution and wheel are written to `src/main/python/dist`. To rebuild only the Python artifacts after the runtime is available, run:

```powershell
Set-Location src/main/python
python -m build
```

## License

Apache License, Version 2.0.
