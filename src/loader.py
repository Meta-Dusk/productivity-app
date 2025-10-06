import sys, os, tempfile

from pathlib import Path
from default_config import DEFAULT_CONFIG
from utilities import get_date
from enum import Enum


# Initial Setup
APP_NAME = "ProductivityApp"

# Detect base directory
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

# Log file (always write to a safe location)
_LOG_FILE = Path(tempfile.gettempdir()) / f"{APP_NAME}_loader.log"

# Reset log contents
with open(_LOG_FILE, "w", encoding="utf-8") as f:
    f.write(f"[{get_date()}] Logs logs logs...\n=====================================\n")

class LogType(Enum):
    WARNING = "warning"
    DEFAULT = "default"
    GOOD = "good"

def _log(msg: str, log_type: LogType = LogType.DEFAULT) -> None:
    """Prints and writes a log."""
    try:
        line = f"[{get_date()}]\t{msg}\n"
        # try to print for dev (console may not exist in packaged app)
        try:
            def printf(output: str):
                print(f"[DEBUG] {output}", flush=True)
            match log_type:
                case LogType.DEFAULT:
                    printf(f"ℹ️  {msg}")
                case LogType.WARNING:
                    printf(f"⚠️ {msg}")
                case LogType.GOOD:
                    printf(f"✅ {msg}")
        except Exception:
            pass
        # append to log file (always safe)
        with open(_LOG_FILE, "a", encoding="utf-8") as fh:
            fh.write(line)
    except Exception:
        # never crash logging
        pass

def can_write_to_dir(path: Path) -> bool:
    """Return True if the process can write to the given directory."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        test_file = path / "_perm_test.tmp"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("test")
        # try to remove (ignore errors)
        try:
            test_file.unlink()
        except Exception:
            pass
        return True
    except Exception as e:
        _log(f"can_write_to_dir({path}) failed: {e}", LogType.WARNING)
        return False

def _choose_writable_root() -> Path:
    """Pick the best writable config directory (APPDATA -> HOME -> temp)."""
    # try APPDATA (roaming)
    try:
        appdata = os.getenv("APPDATA")
    except Exception:
        appdata = None

    candidates = []
    if appdata:
        candidates.append(Path(appdata) / "MetaDusk" / APP_NAME / "config")
    # prefer HOME next
    candidates.append(Path.home() / ".MetaDusk" / APP_NAME / "config")
    # final fallback: OS temp
    candidates.append(Path(tempfile.gettempdir()) / APP_NAME / "config")

    for cand in candidates:
        try:
            if can_write_to_dir(cand):
                _log(f"Selected config root: {cand}", LogType.GOOD)
                return cand
        except Exception as e:
            _log(f"Candidate check failed for {cand}: {e}", LogType.WARNING)

    # as last resort, return the temp path (attempt mkdir, but don't raise)
    final = Path(tempfile.gettempdir()) / APP_NAME / "config"
    try:
        final.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        _log(f"Final mkdir failed for {final}: {e}", LogType.WARNING)
    return final

# determine CONFIG_ROOT and CONFIG_FILE (globals)
CONFIG_ROOT = _choose_writable_root()
OUTPUT_FILE = "output.txt"
CONFIG_FILE = CONFIG_ROOT / OUTPUT_FILE

def ensure_config_exists() -> Path:
    """
    Ensure that a writable config file exists.
    Returns the actual path to the config file that was used.
    This function will never raise an exception (it logs instead).
    """
    global CONFIG_ROOT, CONFIG_FILE

    _log(f"ensure_config_exists() start. BASE_DIR={BASE_DIR} CONFIG_ROOT(candidate)={CONFIG_ROOT}")

    # ensure the directory exists (best-effort)
    try:
        CONFIG_ROOT.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        _log(f"mkdir failed for {CONFIG_ROOT}: {e}", LogType.WARNING)
        # try to pick a safer location (HOME)
        try:
            alt = Path.home() / ".MetaDusk" / APP_NAME / "config"
            alt.mkdir(parents=True, exist_ok=True)
            if can_write_to_dir(alt):
                CONFIG_ROOT = alt
                _log(f"Falling back to HOME config root: {CONFIG_ROOT}")
        except Exception as e2:
            _log(f"Fallback mkdir failed: {e2}", LogType.WARNING)
            # fallback to tempdir
            try:
                tmp = Path(tempfile.gettempdir()) / APP_NAME / "config"
                tmp.mkdir(parents=True, exist_ok=True)
                CONFIG_ROOT = tmp
                _log(f"Falling back to TEMP config root: {CONFIG_ROOT}")
            except Exception as e3:
                _log(f"All mkdir attempts failed: {e3}", LogType.WARNING)
                # still continue; CONFIG_ROOT may be non-writable but we won't raise

    # update CONFIG_FILE to reflect chosen root
    CONFIG_FILE = CONFIG_ROOT / OUTPUT_FILE

    # If file doesn't exist, attempt to create it
    try:
        if not CONFIG_FILE.exists():
            CONFIG_FILE.write_text(DEFAULT_CONFIG, encoding="utf-8")
            _log(f"Created default config at: {CONFIG_FILE}", LogType.GOOD)
        else:
            _log(f"Found existing config at: {CONFIG_FILE}", LogType.GOOD)
    except Exception as e:
        _log(f"Failed to create or write config at {CONFIG_FILE}: {e}", LogType.WARNING)
        # try to write a fallback config inside HOME or temp (guaranteed writable)
        try:
            fallback = Path.home() / ".MetaDusk" / APP_NAME / OUTPUT_FILE
            fallback.parent.mkdir(parents=True, exist_ok=True)
            fallback.write_text(DEFAULT_CONFIG, encoding="utf-8")
            CONFIG_FILE = fallback
            CONFIG_ROOT = fallback.parent
            _log(f"Wrote fallback config at: {fallback}", LogType.GOOD)
        except Exception as e2:
            _log(f"Failed to write fallback config at HOME: {e2}", LogType.WARNING)
            try:
                fallback2 = Path(tempfile.gettempdir()) / APP_NAME / OUTPUT_FILE
                fallback2.parent.mkdir(parents=True, exist_ok=True)
                fallback2.write_text(DEFAULT_CONFIG, encoding="utf-8")
                CONFIG_FILE = fallback2
                CONFIG_ROOT = fallback2.parent
                _log(f"Wrote fallback config at TEMP: {fallback2}", LogType.GOOD)
            except Exception as e3:
                _log(f"Failed to write fallback config at TEMP: {e3}", LogType.WARNING)
                # give up but don't raise; the app should continue with empty lists

    _log(f"ensure_config_exists() complete. Using CONFIG_ROOT={CONFIG_ROOT}, CONFIG_FILE={CONFIG_FILE}", LogType.GOOD)
    return CONFIG_FILE


# --- Load app lists from config ---
def load_app_lists():
    """Load the productive and distracting lists from the config file."""
    productive, distracting, current_section = [], [], None

    if not CONFIG_FILE.exists():
        return productive, distracting

    with CONFIG_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                section = line[1:-1].upper()
                if section == "PRODUCTIVE_APPS":
                    current_section = productive
                elif section == "DISTRACTING_KEYWORDS":
                    current_section = distracting
                else:
                    current_section = None
                continue
            if current_section is not None:
                current_section.append(line.lower())

    return productive, distracting


# --- Test function (for dev use only) ---
def test():
    ensure_config_exists()
    PRODUCTIVE_APPS, DISTRACTING_KEYWORDS = load_app_lists()
    print(f"Productive Apps: {PRODUCTIVE_APPS}")
    print(f"Distracting Keywords: {DISTRACTING_KEYWORDS}")


if __name__ == "__main__":
    test()
