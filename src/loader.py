import sys
from pathlib import Path

# Detect base directory (works in both source and packaged form)
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG_DIR = BASE_DIR / "config"
CONFIG_FILE = CONFIG_DIR / "apps.txt"

DEFAULT_CONFIG = """# ProductivityApp Config
# Lines starting with "#" are comments
# Add more items to each list as you like.

[PRODUCTIVE_APPS]
code.exe
pycharm64.exe
anki.exe
obsidian.exe
notepad.exe
pdfreader.exe
mspowerpoint.exe

[DISTRACTING_KEYWORDS]
youtube
facebook
reddit
twitter
tiktok
discord
netflix
"""

def ensure_config_exists():
    """Ensure that the config file exists next to the executable."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(DEFAULT_CONFIG, encoding="utf-8")
        print(f"🆕 Created default config at: {CONFIG_FILE}")
    else:
        print(f"✅ Loaded config from: {CONFIG_FILE}")

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


# Example Usage
def test():
    ensure_config_exists()
    PRODUCTIVE_APPS, DISTRACTING_KEYWORDS = load_app_lists()
    print(f"Productive Apps: {PRODUCTIVE_APPS}")
    print(f"Distracting Keywords: {DISTRACTING_KEYWORDS}")
    
if __name__ == "__main__":
    test()