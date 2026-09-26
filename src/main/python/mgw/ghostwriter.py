"""Python wrapper for the Ghostwriter Java command-line processor."""

import os
import sys

import jpype
import jpype.imports

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JAR_PATH = os.path.join(BASE_DIR, "jars", "ghostwriter.jar")

def _ensure_jvm_started() -> None:
    """Ensure the JPype JVM is started with the required classpath and valid JAVA_HOME."""
    if jpype.isJVMStarted():
        return

    # 1. Validate that JAVA_HOME is set in the environment
    java_home = os.environ.get("JAVA_HOME")
    if not java_home:
        print(
            "Error: JAVA_HOME environment variable is not set. "
            "Please set JAVA_HOME to your JDK installation path.",
            file=sys.stderr,
        )
        sys.exit(1)

    # 2. Validate that the JAVA_HOME path actually exists on disk
    if not os.path.isdir(java_home):
        print(
            f"Error: JAVA_HOME path does not exist or is not a directory: {java_home}",
            file=sys.stderr,
        )
        sys.exit(1)

    # 3. Optional heuristic check: verify JVM library exists inside JAVA_HOME 
    # (helps catch missing JDK/JRE components early)
    jvm_path = jpype.getDefaultJVMPath()
    if not jvm_path or not os.path.exists(jvm_path):
        print(
            f"Error: Could not locate a valid JVM library using JAVA_HOME={java_home}. "
            f"Resolved path was: {jvm_path}. Ensure a full JDK (not just a JRE) is installed.",
            file=sys.stderr,
        )
        sys.exit(1)

    # 4. Start the JVM
    try:
        jpype.startJVM(
            jvm_path,
            f"-Djava.class.path={JAR_PATH}",
            convertStrings=True,
        )
    except Exception as e:
        print(f"Error: Failed to start the Java Virtual Machine: {e}", file=sys.stderr)
        sys.exit(1)

def gdp(model: str | None = None,
        project_dir: str | None = None,
        path: str = ".",
        config_file: str = "gw.properties") -> list[str]:
    """Process guidance tags in the current project.

    GDP is deliberately kept separate from :func:`gw`: the Java command-line
    entry point handles both guidance processing and acts, whereas this
    function exposes the guidance processor directly for Python callers.
    ``GuidanceProcessor`` requires the project directory, the optional model
    name, and a configurator.  Passing ``None`` for the model lets the Java
    implementation resolve it from its normal configuration sources.
    """
    _ensure_jvm_started()

    from org.machanism.machai.gw.processor import GuidanceProcessor
    from org.machanism.macha.core.commons.configurator import PropertiesConfigurator
    from java.io import File

    if project_dir is None:
        java_project_dir = File(os.path.abspath("."))
    else:
        java_project_dir = File(os.path.abspath(str(project_dir)))

    guidance_processor = GuidanceProcessor(
        java_project_dir,
        model,
        PropertiesConfigurator(config_file),
    )
    guidance_processor.scanDocuments(java_project_dir, path)

    return list(guidance_processor.getReport())

def adw() -> str:
    """Run GDP processor."""
    _ensure_jvm_started()

    # Add your ADW specific invocation logic here
    # from org.machanism.machai.gdp.processor import ActProcessor
    # ...
    # return result

    raise NotImplementedError("ADW implementation pending")


def gw(args: list[str] | None = None) -> str:
    """Run Ghostwriter from Python or as the installed console script."""
    if args is None:
        args = sys.argv[1:]

    _ensure_jvm_started()

    from org.machanism.machai.gw.processor import Ghostwriter

    result = Ghostwriter.main(args)
    return result


if __name__ == "__main__":
    gw()
