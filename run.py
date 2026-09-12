"""
Bujji Launcher Entry Point.
Allows running Bujji directly from the root with: python run.py
"""

from pathlib import Path
import sys

# Ensure root directory is on sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from bujji.main import main

if __name__ == "__main__":
    main()
