"""
Automated build script for the app. Use `-h` or `--help` for available flags.

Steps:
    1. Run bump_build.py to update build_number.
    2. Run Either build or pack with Flet (Including icon).
    3. Optionally compile installer with Inno Setup (Available only for Flet build).

Syntax:
    build_app.py [OPTIONS]
    i.e.: `uv run py .\tools\build_app.py -h`

Usage:
    (Remove `uv run` if not using uv)
    `uv run py -m tools.build_app`
    or
    `uv run py .\tools\build_app.py`
"""

import subprocess, sys, argparse, tomlkit, time, re
from pathlib import Path
from colorama import Fore, Style, init as colorama_init
from dataclasses import dataclass


APP_NAME = "ProductivityApp"

# Initialize colorama (auto resets colors after each print)
colorama_init(autoreset=True)


# === PATHS ===
ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
INSTALLER = ROOT / "installer" / "productivity.iss"
PYPROJECT = ROOT / "pyproject.toml"
BUMP_SCRIPT = TOOLS / "bump_build.py"
BUILD_DIR = ROOT / "build" / "windows"
DIST_DIR = ROOT / "dist"
ICON_DIR = ROOT / "src" / "assets" / "images" / "icon.ico"
SCRIPT = ROOT / "src" / "main.py"

# === PARSER SETUP ===
@dataclass
class Config:
    no_build: bool
    no_installer: bool
    pack: bool
    dry_run: bool

parser = argparse.ArgumentParser(description=f"Automated Flet build script for {APP_NAME}.")
parser.add_argument("-b", "--no-build", action="store_true", help="Only bump build number without building.")
parser.add_argument("-i", "--no-installer", action="store_true", help="Skip Inno Setup installer compilation.")
parser.add_argument("-p", "--pack", action="store_true", help="Only use flet pack for packaging the app. Will ignore installer.")
parser.add_argument("-d", "--dry-run", action="store_true", help="Show commands without executing.")
args = parser.parse_args()
config = Config(**vars(args))


# === UTILITIES ===
def humanize_name(s: str) -> str:
    s = re.sub(r'[_\-]+', ' ', s)               # replace underscores/dashes with space
    s = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', s)  # only split lower -> Upper
    return s.strip().title()                    # clean + Title Case

def print_section(title: str):
    """Pretty print a centered section header."""
    bar = f"{Fore.CYAN}{'=' * 50}"
    centered = f"{Fore.CYAN}{title.center(50)}"
    print(f"\n{bar}\n{centered}\n{bar}")

def print_block(text: str, color=Fore.WHITE):
    """Print a multi-line block of text cleanly."""
    print(f"\n{color}{text.strip()}\n")
    
def print_warning(text: str, color=Fore.YELLOW):
    print(f"⚠️  {color}{text}")

def print_info(text: str, color=Fore.LIGHTBLUE_EX, style=Style.BRIGHT):
    print(f"ℹ️  {color}{style}{text}")


class BuildError(Exception):
    def __init__(self, message: str, code: int = 1):
        super().__init__(message)
        self.code = code  # store the return/exit code

def run(cmd: list[str], cwd: Path | None = None):
    """Run a shell command and stream output."""
    print(f"\n{Fore.BLUE}🟦 Running: {Style.BRIGHT}{' '.join(cmd)}\n")
    if config.dry_run:
        print_info("Dry run mode: command not executed.")
        return
    result = subprocess.run(cmd, cwd=cwd or ROOT)
    if result.returncode != 0:
        print(f"{Fore.RED}❌ Command failed with exit code {result.returncode}: {' '.join(cmd)}")
        raise BuildError(
            f"Command failed: {' '.join(cmd)} (exit {result.returncode})",
            code=result.returncode
        )
    print(f"{Fore.GREEN}✅ Done.")


@dataclass
class BuildInfo:
    version: str
    description: str
    build_number: int
    file_version: str
    company_name: str
    copyright: str

def get_build_info() -> BuildInfo:
    """Read build-related information from pyproject.toml with type safety."""
    if not PYPROJECT.exists():
        print(f"{Fore.RED}❌ pyproject.toml not found.")
        sys.exit(1)

    doc = tomlkit.parse(PYPROJECT.read_text(encoding="utf-8"))

    project = doc.get("project", {})
    tool_flet = doc.get("tool", {}).get("flet", {})

    version = project.get("version", "0.0.0")
    description = project.get("description", "unknown")
    build_number = tool_flet.get("build_number", 0)
    company_name = tool_flet.get("company", "unknown")
    copyright = tool_flet.get("copyright", "unknown")

    file_version = f"{version}.{build_number}"

    return BuildInfo(
        version=version,
        description=description,
        build_number=build_number,
        file_version=file_version,
        company_name=company_name,
        copyright=copyright
    )
    

# === MAIN BUILD PROCESS ===
def main():
    # Start timer
    start_time = time.perf_counter()

    # Step 1: Initial info
    info = get_build_info()
    print_section("🚀 BUILDING PRODUCTIVITY APP")
    print_block(f"""
📦 Version: {info.version}
🔢 Build number (before): {info.build_number}
    """, color=Fore.LIGHTWHITE_EX)

    # Step 2: Bump build number
    print_section("STEP 1: BUMP BUILD NUMBER")
    run([sys.executable, str(BUMP_SCRIPT)])
    info = get_build_info()

    # Step 3: Build app (unless skipped)
    if not config.no_build and not config.pack:
        print_section("STEP 2: BUILDING FLET APP FOR WINDOWS")
        build_cmd = ["uv", "run", "flet", "build", "windows", "-v"]
        run(build_cmd)

        if BUILD_DIR.exists():
            print_block(f"📁 Build output located at:\n{BUILD_DIR}", color=Fore.CYAN)
        else:
            print_warning("No build directory found after build.")
    elif config.pack:
        print_section("STEP 2: BUILDING FLET APP FOR WINDOWS WITH PACK")
        build_options = [
            "--icon", ICON_DIR.as_posix(),
            "--name", f"{APP_NAME}.v{info.version}-Win64-Standalone",
            "--product-name", humanize_name(APP_NAME),
            "--file-description", info.description,
            "--product-version", info.version,
            "--file-version", info.file_version,
            "--company-name", info.company_name,
            "--copyright", info.copyright
        ]
        build_cmd = ["uv", "run", "flet", "pack", *build_options, SCRIPT.as_posix()]
        run(build_cmd)
    else:
        print_info("Skipping app build (--no-build flag used).")

    # Step 4: Build installer (if requested)
    if not config.no_installer and INSTALLER.exists() and not config.pack:
        print_section("STEP 3: BUILD INSTALLER")
        inno_output_dir = ROOT / "dist" / "installer"
        inno_output_dir.mkdir(parents=True, exist_ok=True)

        version_tag = f"{APP_NAME}-v{info.version}-Win64-Installer"
        inno_cmd = [
            "iscc",
            f"/O{inno_output_dir}",            # Output folder
            f"/DMyAppVersion={info.version}",  # Pass version from pyproject.toml
            str(INSTALLER)
        ]
        run(inno_cmd)

        output_exe = inno_output_dir / f"{version_tag}.exe"
        if output_exe.exists():
            print_block(f"🎉 Installer created:\n{output_exe}", color=Fore.GREEN)
        elif not config.dry_run:
            print_warning("Installer compilation finished, but file not found.")
    elif config.no_installer:
        print_info("Skipping installer build (--no-installer flag used).")
    else:
        print_warning("No Inno Setup script found, skipping installer build.")

    # Step 5: Summary
    elapsed = time.perf_counter() - start_time
    print_section("✅ BUILD SUMMARY")
    print_block(f"""
📦 Version: {info.version}
🔢 Build number: {info.build_number}
⏱️  Elapsed time: {elapsed:.2f} seconds

🎉 Build process completed successfully!
    """, color=Fore.GREEN)


if __name__ == "__main__":
    try:
        main()
    except BuildError as e:
        print_warning(e)
        sys.exit(e.code)