<!--@guidance:
You are an expert Python packaging assistant. Using general knowledge and the provided reference guide for building and publishing the  
Python package (which includes a Java/JPype component and installs that), 
generate a concise and clear explanation or tutorial covering:

1. Prerequisites & Tooling (Python, Maven, Build/Twine)
2. Building distributions (based on project review)
3. Validation and Testing (`twine check` and local wheel installation)
4. Publishing to TestPyPI and PyPI
5. Installing and verifying the package from TestPyPI and PyPI

Keep the output minimal, structured, and easy to read with code blocks where appropriate.
-->

# Build and publish

## Prerequisites and tooling

Use Python 3.9 or newer, a JDK compatible with the Maven build (the project targets
Java 17), and Maven. `build` creates the Python source distribution and wheel;
`twine` validates and uploads them:

```powershell
python --version
mvn --version
python -m pip install --upgrade build twine
```

The package depends on `jpype1>=1.4.0`. Ensure Java is discoverable (set
`JAVA_HOME` if necessary) because the bundled Java runtime is started through JPype.

## Build the distributions

From the project root, first assemble the Java runtime. Maven places
`ghostwriter.jar` in `mgw/jars`, and the Hatchling wheel configuration includes it
in the Python package:

```powershell
mvn clean package
python -m build
```

The resulting files are written to `dist/` (a `.tar.gz` source distribution and a
`.whl` wheel). Remove stale files from `dist/` before rebuilding a release.

## Validate and test locally

Check the distribution metadata, then install the wheel in a clean virtual
environment and exercise both the import and the bundled runtime:

```powershell
python -m twine check dist/*
python -m venv .venv-release
.\.venv-release\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install (Get-ChildItem dist\*.whl | Select-Object -First 1).FullName
python -c "from mgw import gw; print(gw(['--help']))"
```

Deactivate and remove the temporary environment when testing is complete:

```powershell
deactivate
Remove-Item -Recurse -Force .venv-release
```

## Publish to TestPyPI and PyPI

Configure a TestPyPI API token through Twine's supported credentials mechanism
(rather than committing credentials), then upload both artifacts:

```powershell
python -m twine upload --repository testpypi dist/*
```

After confirming the TestPyPI installation works, upload the same version to PyPI:

```powershell
python -m twine upload dist/*
```

A version already uploaded to either index cannot be overwritten; update the
version in `pyproject.toml` and rebuild if a release must be corrected.

## Install and verify

Use an isolated environment for each index. TestPyPI may need the public PyPI
index as an additional source for dependencies such as JPype1:

```powershell
python -m venv .venv-testpypi
.\.venv-testpypi\Scripts\Activate.ps1
python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ mgw==1.4.2.1
python -c "from mgw import gw; print(gw(['--help']))"
deactivate

python -m venv .venv-pypi
.\.venv-pypi\Scripts\Activate.ps1
python -m pip install mgw==1.4.2.1
python -c "from mgw import gw; print(gw(['--help']))"
deactivate
```

Replace `1.4.2.1` with the version being released. Successful installation and
`gw(['--help'])` output verify that Python dependencies, the bundled JAR, JPype,
and Java runtime discovery all work from the published package.
