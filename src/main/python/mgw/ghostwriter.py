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
        config_file: str = "gw.properties",
        instructions: str | None = None,
        threads: int | None = None,
        excludes: list[str] | None = None,
        non_recursive: bool = False,
        module_thread_timeout_minutes: int | None = None) -> list[str]:
    """Process guidance tags in the current project.

    GDP is deliberately kept separate from :func:`gw`: the Java command-line
    entry point handles both guidance processing and acts, whereas this
    function exposes the guidance processor directly for Python callers.
    ``GuidanceProcessor`` requires the project directory, the optional model
    name, and a configurator.  Passing ``None`` for the model lets the Java
    implementation resolve it from its normal configuration sources.  The
    optional processor settings map to the public inherited API documented by
    Ghostwriter's bindex: thread count, exclusions, non-recursive traversal,
    and module timeout.  ``path`` is passed unchanged as a relative path,
    glob, or regular-expression matcher.
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

    if instructions is not None:
        guidance_processor.setInstructions(str(instructions))
    if threads is not None:
        if isinstance(threads, bool) or not isinstance(threads, int) or threads <= 0:
            raise ValueError("threads must be a positive integer")
        guidance_processor.setThreads(threads)
    if excludes is not None:
        if isinstance(excludes, (str, bytes)):
            raise TypeError("excludes must be a list of path patterns")
        guidance_processor.setExcludes([str(pattern) for pattern in excludes])
    guidance_processor.setNonRecursive(bool(non_recursive))
    if module_thread_timeout_minutes is not None:
        if (isinstance(module_thread_timeout_minutes, bool)
                or not isinstance(module_thread_timeout_minutes, int)
                or module_thread_timeout_minutes <= 0):
            raise ValueError("module_thread_timeout_minutes must be a positive integer")
        guidance_processor.setModuleThreadTimeoutMinutes(module_thread_timeout_minutes)

    guidance_processor.scanDocuments(java_project_dir, path)

    return list(guidance_processor.getReport())

def adw(
        act: str,
        model: str | None = None,
        project_dir: str | None = None,
        path: str = ".",
        config_file: str = "gw.properties",
        acts_location: str | None = None,
        interactive: bool = False,
        disable_normal_order: bool = False) -> list[str]:
    """Execute an Act against the current project.

    This is the Python equivalent of Ghostwriter's ``--act`` mode.  ``act``
    is the Act name (or an Act expression understood by Java), while
    ``path`` is a project-relative path or matcher.  The Java implementation
    performs Act loading and episode selection; this wrapper intentionally
    leaves that syntax untouched.

    ``ActProcessor`` is constructed with the same three values documented by
    the Ghostwriter bindex: project directory, provider/model identifier, and
    configurator.  ``None`` for ``model`` preserves the Java configurator's
    normal model resolution behaviour.

    The returned value is a Python list containing the processor's results.
    Java ``List`` values are converted explicitly so callers do not need to
    know about JPype collections.
    """
    if not isinstance(act, str) or not act.strip():
        raise ValueError("act must be a non-empty Act name or expression")

    _ensure_jvm_started()

    from java.io import File
    from org.machanism.machai.gw.processor import ActProcessor
    from org.machanism.macha.core.commons.configurator import PropertiesConfigurator

    java_project_dir = File(
        os.path.abspath("." if project_dir is None else str(project_dir))
    )
    processor = ActProcessor(
        java_project_dir,
        model,
        PropertiesConfigurator(config_file),
    )

    if acts_location is not None:
        processor.setActsLocation(str(acts_location))
    processor.setAct(act)
    processor.setInteractive(bool(interactive))
    processor.setDisableNormalOrder(bool(disable_normal_order))

    # ActProcessor inherits scanDocuments from AIFileProcessor.  Unlike
    # processProjectDir, this entry point accepts the path string directly
    # and lets the Java processor create the appropriate project layout.
    processor.scanDocuments(java_project_dir, path)
    return list(processor.getResults())


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
