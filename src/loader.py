import sys, os, tempfile, tomllib
from pathlib import Path
from default_config import DEFAULT_CONFIG
from utilities import get_date
from enum import Enum
from core.data_types import WindowNames, Productive, Distracting
from smart_classifier import SmartClassifier
from window import WindowHelperManager
from functools import cache


# === Initial Setup ===
APP_NAME = "ProductivityApp"

# Detect base directory
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

# Log file (always write to a safe location)
LOG_DIR = Path(tempfile.gettempdir())
LOG_FILE = LOG_DIR / f"{APP_NAME}_loader.log"

# Reset log contents
with open(LOG_FILE, "w", encoding="utf-8") as lf:
    lf.write(f"[{get_date()}] Logs for {APP_NAME}\n{'=' * 50}\n")


# === Logging System ===
class LogType(Enum):
    WARNING = "warning"
    DEFAULT = "default"
    GOOD = "good"


def _log(msg: str, log_type: LogType = LogType.DEFAULT) -> None:
    """Prints and writes a log."""
    try:
        line = f"[{get_date()}]\t{msg}\n"

        def printf(output: str):
            print(f"[DEBUG] {output}", flush=True)

        match log_type:
            case LogType.DEFAULT:
                printf(f"ℹ️  {msg}")
            case LogType.WARNING:
                printf(f"⚠️ {msg}")
            case LogType.GOOD:
                printf(f"✅ {msg}")

        with open(LOG_FILE, "a", encoding="utf-8") as lf:
            lf.write(line)
    except Exception:
        pass  # never crash logging


# === Directory + Config Management ===
def can_write_to_dir(path: Path) -> bool:
    """Return True if the process can write to the given directory."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        if path.exists() and not os.access(path, os.W_OK):
            return False

        with tempfile.NamedTemporaryFile(dir=path, delete=True) as tmp:
            tmp.write(b"test")
            tmp.flush()
        return True

    except Exception as e:
        _log(f"can_write_to_dir({path}) failed: {e}", LogType.WARNING)
        return False


@cache # Cache result just in case it'll be called multiple times
def _choose_writable_root() -> Path:
    """Pick the best writable config directory (APPDATA -> HOME -> temp)."""
    appdata = os.getenv("APPDATA", None)

    candidates = []
    if appdata:
        candidates.append(Path(appdata) / "MetaDusk" / APP_NAME / "config")
    candidates.append(Path.home() / ".MetaDusk" / APP_NAME / "config")
    candidates.append(Path(tempfile.gettempdir()) / APP_NAME / "config")

    for cand in candidates:
        if can_write_to_dir(cand):
            _log(f"Selected config root: {cand}", LogType.GOOD)
            return cand

    final = Path(tempfile.gettempdir()) / APP_NAME / "config"
    final.mkdir(parents=True, exist_ok=True)
    return final


CONFIG_ROOT = _choose_writable_root()
CONFIG_FILE_NAME = "config.toml"
CONFIG_PATH = CONFIG_ROOT / CONFIG_FILE_NAME


def reset_config() -> bool:
    """Reset contents of the config file to the default TOML template."""
    try:
        CONFIG_PATH.write_text(DEFAULT_CONFIG, encoding="utf-8")
        _log(f"Config reset to default at: {CONFIG_PATH}", LogType.GOOD)
        return True
    except Exception as e:
        _log(f"Failed to reset config: {e}", LogType.WARNING)
        return False


def ensure_config_exists() -> Path:
    """Ensure that a writable config file exists, and populate it if missing."""
    global CONFIG_PATH, CONFIG_ROOT

    _log(f"ensure_config_exists() start. BASE_DIR={BASE_DIR} CONFIG_ROOT={CONFIG_ROOT}")

    CONFIG_ROOT.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH = CONFIG_ROOT / CONFIG_FILE_NAME

    # Create config file if missing
    if not CONFIG_PATH.exists():
        _log("Config file not found. Creating default one...", LogType.WARNING)
        reset_config()
    else:
        _log(f"Config file found: {CONFIG_PATH}", LogType.GOOD)

    _log(f"ensure_config_exists() complete. Using CONFIG_PATH={CONFIG_PATH}", LogType.GOOD)
    return CONFIG_PATH


# === TOML-Based Config Loader ===
def load_app_lists() -> WindowNames:
    """
    Load the productive and distracting apps/keywords from the TOML config.
    Returns: (productive_apps, productive_keywords, distracting_apps, distracting_keywords)
    """
    ensure_config_exists()

    try:
        with CONFIG_PATH.open("rb") as f:
            data = tomllib.load(f)

        prod = data.get("PRODUCTIVE", {})
        dist = data.get("DISTRACTING", {})

        window_names = WindowNames(
            productive=Productive(
                apps=[x.lower() for x in prod.get("apps", [])],
                keywords=[x.lower() for x in prod.get("keywords", [])],
            ),
            distracting=Distracting(
                apps=[x.lower() for x in dist.get("apps", [])],
                keywords=[x.lower() for x in dist.get("keywords", [])],
            ),
        )

        _log("Successfully loaded app lists from TOML.", LogType.GOOD)

        return window_names

    except Exception as e:
        _log(f"Failed to parse config TOML: {e}", LogType.WARNING)
        return WindowNames()


# === Dev Test ===
def test():
    def print_items(label: str, list: list):
        print(f"{label}: {", ".join([item for item in list])}\n")
    
    ensure_config_exists()
    data_list = load_app_lists()
    classifier = SmartClassifier(data_list)
    window_manager = WindowHelperManager()
    info = window_manager.get_latest_window_info()
    result = classifier.classify(info)
    
    print_items("\nProductive Apps", data_list.productive.apps)
    print_items("Productive Keywords", data_list.productive.keywords)
    print_items("Distracting Apps", data_list.distracting.apps)
    print_items("Distracting Keywords", data_list.distracting.keywords)
    print(f"Classifier Test: {result}\n")
    

if __name__ == "__main__":
    test()
