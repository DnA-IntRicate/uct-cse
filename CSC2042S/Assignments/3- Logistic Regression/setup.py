import subprocess
import os
import sys
from pathlib import Path

REQS_FILE = Path("requirements.txt")

def install_requirements():
    print("\nInstalling dependencies from requirements.txt...\n")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "-r", str(REQS_FILE)])
        print("\nAll dependencies installed successfully.")

    except subprocess.CalledProcessError as e:
        sys.exit(f"Failed to install dependencies. Pip exited with code {e.returncode}!")

def main():
    choice = input("Would you like to install the required modules? (y/n): ")

    if choice.lower() == "y":
        install_requirements()

    if not os.path.isdir("data"):
        print("\nMasakhane repo dataset not found!")
        subprocess.run(["git", "clone", "https://github.com/masakhane-io/masakhane-news.git", "data"])
    else:
        print("\nMasakhane repo dataset located.")

if __name__ == "__main__":
    main()
    input("Press Enter to continue...")
