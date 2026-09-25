# Build and publish `machai-gw`

This document describes how to build the Python distribution and publish it to
[TestPyPI](https://test.pypi.org/).

## Prerequisites

- Python 3.9 or newer
- A Java runtime compatible with the bundled Ghostwriter JAR
- A TestPyPI account
- A TestPyPI API token
- From the project root (`.`), install the packaging tools:

```bash
python -m pip install --upgrade build twine
```

On Windows, use `py` instead of `python` if that is the Python launcher used by
your installation.

## Install and run

### Install from the local build

After building the wheel, create a virtual environment and install the package
from the `dist/` directory:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Or activate it on Windows Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

Install the wheel and its dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install dist/machai_gw-1.4.2.0-py3-none-any.whl
```

The package requires Java at runtime because it starts the bundled
Ghostwriter JAR through JPype. If Java is not found automatically, set
`JAVA_HOME` to a JDK or JRE installation. In PowerShell:

```powershell
$env:JAVA_HOME = "C:\Path\To\Your\JDK"
```

### Run the installed command

The package installs the `machai-gw` command. Pass Ghostwriter arguments after
the command name:

```bash
machai-gw --help
```

You can also invoke the module directly:

```bash
python -m machai.gw --help
```

The wrapper can be used from Python as well:

```python
from machai.gw import gw

result = gw(["--help"])
print(result)
```

### Install and run the TestPyPI package

After uploading a release, install it from TestPyPI. The extra index is needed
because dependencies such as `jpype1` are hosted on the regular PyPI index:

```bash
python -m pip install \
    --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    machai-gw==1.4.2.0
```

Then run it in the same activated environment:

```bash
machai-gw --help
```

## 1. Build the distributions

The Maven build updates the bundled Java artifact in `machai/gw/jars/`. Run it
first when the Java artifact needs to be rebuilt:

```bash
mvn clean package
```

Then create the Python source distribution and wheel:

```bash
python -m build
```

The resulting files are written to `dist/`, for example:

```text
dist/machai_gw-1.4.2.0.tar.gz
dist/machai_gw-1.4.2.0-py3-none-any.whl
```

The wheel should contain the Python package and the bundled
`machai/gw/jars/ghostwriter.jar` file.

To remove old distributions before rebuilding, use the following commands in
PowerShell:

```powershell
Remove-Item -Recurse -Force dist, build -ErrorAction SilentlyContinue
Get-ChildItem -Filter "*.egg-info" -Directory | Remove-Item -Recurse -Force
python -m build
```

## 2. Check the distributions

Validate the package metadata and archive contents:

```bash
python -m twine check dist/*
```

Install the wheel locally in a clean virtual environment and verify the console
command:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install dist/machai_gw-1.4.2.0-py3-none-any.whl
machai-gw --help
```

The wrapper requires a Java runtime. Set `JAVA_HOME` if JPype cannot locate the
JVM automatically. For example, in PowerShell:

```powershell
$env:JAVA_HOME = "C:\Path\To\Your\JDK"
```

## 3. Upload to TestPyPI

Upload both distribution files using the TestPyPI repository URL:

```bash
python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

When prompted, enter:

- Username: `__token__`
- Password: your TestPyPI API token

Do not commit the token to the repository or place it directly in this file.

For non-interactive use, configure a `.pypirc` file outside version control or
use environment variables supported by your CI system. A `.pypirc` entry can
look like this:

```ini
[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = <your TestPyPI token>
```

Keep the token value private and add any local credential file to `.gitignore`.

## 4. Install from TestPyPI

TestPyPI is separate from the production Python Package Index, so install the
package with the TestPyPI index explicitly. Dependencies such as `jpype1` are
normally fetched from the regular PyPI index:

```bash
python -m venv .venv-test
.venv-test\Scripts\activate
python -m pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ machai-gw==1.4.2.0
```

On Windows Command Prompt, use one line if the continuation character is not
available:

```cmd
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ machai-gw==1.4.2.0
```

Then test the installed command:

```bash
machai-gw --help
```

The package page will be available at:

```text
https://test.pypi.org/project/machai-gw/
```

## Publishing a later version

PyPI repositories do not allow overwriting an existing release file. Before
publishing again, update the `project.version` value in `pyproject.toml`, then
run the build, validation, and upload steps again:

```bash
python -m build
python -m twine check dist/*
python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

Make sure `dist/` contains only the distributions for the new version before
uploading.
