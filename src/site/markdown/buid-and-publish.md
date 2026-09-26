<!--@guidance:
You are an expert Python packaging and Java integration assistant. Using general knowledge and the provided reference guide for building and publishing a hybrid Python-Java package (containing a Java backend bundled via a JAR, wrapped with JPype, and exposing a console command), generate a concise, step-by-step tutorial covering:

1. Prerequisites & Tooling (Python, Java/JDK, Maven, build, twine)
2. Building Distributions (running Maven to package the JAR, then building Python sdist/wheel)
3. Validation & Local Testing (using `twine check` and testing the local wheel in a virtual environment)
4. Publishing to TestPyPI and Production PyPI (using twine and API tokens)
5. Installing & Verifying from Repositories (handling index fallbacks for dependencies like jpype1)
6. Execution Guidelines (how to invoke the tool via console script, python module, or code API, including JAVA_HOME handling)
   - `python -m twine upload -r testpypi dist/*` 
   - `pip install -U -no-cache-dir -i https://test.pypi.org/simple/ mgw`

Requirements for the output:
- Provide all terminal code blocks and automation steps specifically tailored for the **Windows Command Prompt (batch/cmd)** using standard `.bat` 
  syntax (e.g., using `set`, `python -m venv`, and `.venv\Scripts\activate.bat`).
- Keep the output minimal, highly structured, and easy to follow with clean code blocks.
-->

# Build and publish

## Prerequisites and tooling

Use Python 3.9 or newer, a JDK compatible with the Maven build (the project targets
Java 17), and Maven. `build` creates the Python source distribution and wheel;
`twine` validates and uploads them. Run the following commands from a Windows
Command Prompt:

```bat
python --version
mvn --version
python -m pip install --upgrade build twine
```

The package depends on `jpype1>=1.4.0`. Ensure Java is discoverable because the
bundled Java runtime is started through JPype. If `JAVA_HOME` is not already set,
set it to the JDK installation directory (not a JRE):

```bat
set "JAVA_HOME=C:\Program Files\Java\jdk-17"
set "PATH=%JAVA_HOME%\bin;%PATH%"
```

## Build the distributions

From the project root, first assemble the Java runtime. Maven places
`ghostwriter.jar` in `src/main/python/mgw/jars`, and the Hatchling wheel
configuration includes it in the Python package. The release profile also runs
the Python build; the explicit commands below make both steps clear:

```bat
mvn clean package -Prelease
cd src\main\python
python -m build
```

The resulting files are written to `dist/` (a `.tar.gz` source distribution and a
`.whl` wheel). Remove stale files from `dist/` before rebuilding a release.

## Validate and test locally

Run the following from `src\main\python`. Check the distribution metadata, then
install the wheel in a clean virtual environment and exercise both the import and
the bundled runtime:

```bat
python -m twine check dist/*
python -m venv .venv-release
.venv-release\Scripts\activate.bat
python -m pip install --upgrade pip
for %%F in (dist\*.whl) do python -m pip install "%%F"
python -c "from mgw import gw; print(gw(['--help']))"
```

Deactivate and remove the temporary environment when testing is complete:

```bat
deactivate
rmdir /s /q .venv-release
```

## Publish to TestPyPI and PyPI

Configure a TestPyPI API token through Twine's supported credentials mechanism
(rather than committing credentials). In the current Command Prompt session, you
can provide the token through environment variables:

```bat
set "TWINE_USERNAME=__token__"
set "TWINE_PASSWORD=PASTE_TESTPYPI_API_TOKEN_HERE"
python -m twine upload -r testpypi dist/*
```

After confirming the TestPyPI installation works, upload the same version to PyPI:

```bat
set "TWINE_USERNAME=__token__"
set "TWINE_PASSWORD=PASTE_PYPI_API_TOKEN_HERE"
python -m twine upload dist/*
```

A version already uploaded to either index cannot be overwritten; update the
version in `pyproject.toml` and rebuild if a release must be corrected.

## Install and verify

Use an isolated environment for each index. TestPyPI may need the public PyPI
index as an additional source for dependencies such as JPype1. The pip option is
spelled `--no-cache-dir` (with two hyphens):

```bat
python -m venv .venv-testpypi
.venv-testpypi\Scripts\activate.bat
python -m pip install -U --no-cache-dir -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ mgw==1.4.2.1
python -c "from mgw import gw; print(gw(['--help']))"
deactivate

python -m venv .venv-pypi
.venv-pypi\Scripts\activate.bat
python -m pip install mgw==1.4.2.1
python -c "from mgw import gw; print(gw(['--help']))"
deactivate
```

Replace `1.4.2.1` with the version being released. Successful installation and
`gw(['--help'])` output verify that Python dependencies, the bundled JAR, JPype,
and Java runtime discovery all work from the published package.

## Execution guidelines

With the virtual environment activated and `JAVA_HOME` set to the JDK directory,
the installed console script, Python module, and code API provide equivalent
entry points. This wrapper requires `JAVA_HOME`; it does not fall back to a
system Java installation when that variable is unset:

```bat
mgw --help
python -m mgw --help
python -c "from mgw import gw; print(gw(['--help']))"
```

The wrapper locates the bundled JAR automatically and uses the JDK selected by
`JAVA_HOME` to start JPype. If Java is not found, set `JAVA_HOME` and prepend
its `bin` directory to `PATH` before invoking any entry point:

```bat
set "JAVA_HOME=C:\Program Files\Java\jdk-17"
set "PATH=%JAVA_HOME%\bin;%PATH%"
mgw --help
```
