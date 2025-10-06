import shutil
import site
from pathlib import Path
from colorama import Fore, init as colorama_init

"""
This is an attempt for fixing the missing modules after using `flet build`.
It doesn't work... Just use `flet pack` instead from now on.
"""

colorama_init(autoreset=True)

ROOT = Path(__file__).resolve().parent.parent
APP_DIR = ROOT / "build" / "windows" # Path to executable directory


def copy_pywin32_dlls(target_dir: Path):
    site_packages = Path(site.getsitepackages()[0])
    dlls = ["pythoncom313.dll", "pywintypes313.dll"]  # adjust to your Python version
    
    if not target_dir.exists():
        print(f"{Fore.RED}⚠️ Path does not exist!")
    
    for dll in dlls:
        src = site_packages / "Lib" / "site-packages" / "pywin32_system32" / dll
        if src.exists():
            print(f"{Fore.GREEN}Copying {src.name} → {target_dir}")
            shutil.copy(src, target_dir)
        else:
            print(f"{Fore.RED}⚠️ Missing: {src}")

if __name__ == "__main__":
    copy_pywin32_dlls(APP_DIR)
