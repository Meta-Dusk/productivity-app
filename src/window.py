import json, subprocess
from pathlib import Path
from typing import Optional
from data_types import WindowInfo


HELPER_PATH = Path(__file__).parent / "bin" / "window_helper.exe"
DEBUG_MODE = __debug__


# === MAIN FUNCTIONS ===
def get_active_window_info() -> dict[WindowInfo, Optional[str | int]]:
    """Uses external helper to fetch window info."""
    if not HELPER_PATH.exists():
        print("⚠️  Helper executable not found:", HELPER_PATH)
        return {
            WindowInfo.NAME: "UnknownApp",
            WindowInfo.CLASS_NAME: "None",
            WindowInfo.PROCESS_ID: 0,
        }

    try:
        result = subprocess.run(
            [str(HELPER_PATH), "window_info"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        data = json.loads(result.stdout)
        return {
            WindowInfo.NAME: data.get("name"),
            WindowInfo.CLASS_NAME: data.get("class_name"),
            WindowInfo.PROCESS_ID: data.get("pid"),
        }
    except Exception as e:
        print(f"⚠️  Failed to run window helper: {e}")
        return {
            WindowInfo.NAME: None,
            WindowInfo.CLASS_NAME: None,
            WindowInfo.PROCESS_ID: 0,
        }

def get_process_name(process_id: int) -> str:
    """We already include process name in the helper output."""
    return "N/A"  # (kept for interface compatibility)


# === TESTERS ===
def test_window_helper(verbose: bool = True) -> bool:
    """
    Tests whether the window_helper executable is available and working.
    Returns True if successful, False otherwise.
    """
    import json
    import subprocess

    if not HELPER_PATH.exists():
        if verbose:
            print(f"❌ Helper not found at: {HELPER_PATH}")
        return False

    try:
        result = subprocess.run(
            [str(HELPER_PATH), "window_info"],
            capture_output=True,
            text=True,
            timeout=3,
        )

        if result.returncode != 0:
            if verbose:
                print(f"⚠️ Helper returned non-zero code: {result.returncode}")
                print("stderr:", result.stderr)
            return False

        # Try parsing JSON output
        data = json.loads(result.stdout)
        expected_keys = {"name", "class_name", "pid"}

        if not expected_keys.issubset(data.keys()):
            if verbose:
                print(f"⚠️ Invalid helper output: {data}")
            return False

        if verbose:
            print("✅ Helper test passed.")
            print(f"Active window: {data.get('name')} (PID: {data.get('pid')})")

        return True

    except Exception as e:
        if verbose:
            print(f"❌ Exception while testing helper: {e}")
        return False

# Run this file to test if the helper works.
if __name__ == "__main__":
    if DEBUG_MODE:
        print("Running in debug mode!")
    test_window_helper(verbose=DEBUG_MODE)