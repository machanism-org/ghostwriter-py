import os
import sys
import jpype
import jpype.imports

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JAR_PATH = os.path.join(BASE_DIR, "jars", "ghostwriter.jar")

def gw(args: list[str]) -> str:
    if not jpype.isJVMStarted():
        jpype.startJVM(
            jpype.getDefaultJVMPath(),
            f"-Djava.class.path={JAR_PATH}",
            convertStrings=True
        )
    
    from org.machanism.machai.gw.processor import Ghostwriter
    
    result = Ghostwriter.main(args)
    return result
    
if __name__ == "__main__":
    gw(sys.argv[1:])