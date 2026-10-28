import subprocess
import os

myDir = os.path.dirname(os.path.abspath(__file__))
projRoot = os.path.abspath(os.path.join(myDir, ".."))
os.chdir(projRoot)

subprocess.run(
    ["make", "-C", "./ImageCompare", "run", "ARGS=../bin/Serial/visualiseSearch.png ../bin/Parallel/visualiseSearch.png"],
    check=True, text=True)

print()

subprocess.run(
    ["make", "-C", "./ImageCompare", "run", "ARGS=../bin/Serial/visualiseSearchPath.png ../bin/Parallel/visualiseSearchPath.png"],
    check=True, text=True)

input("Press Enter to continue...")
