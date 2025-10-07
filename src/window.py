import json, subprocess, sys
from pathlib import Path
from typing import Optional
from data_types import WindowInfo


# === MAIN FUNCTIONS ===
def get_helper_path() -> Path:
    if getattr(sys, "frozen", False):
        base_dir = Path(sys.executable).resolve().parent
    else:
        base_dir = Path(__file__).resolve().parent
    helper_path = base_dir / "assets" / "bin" / "window_helper.exe"
    return helper_path

def get_active_window_info() -> dict[WindowInfo, Optional[str | int]]:
    """Uses external helper to fetch window info."""
    helper_path = get_helper_path()
    if not helper_path.exists():
        print("⚠️  Helper executable not found:", helper_path)
        return {
            WindowInfo.NAME: "UnknownApp",
            WindowInfo.CLASS_NAME: "None",
            WindowInfo.PROCESS_ID: 0,
        }

    try:
        result = subprocess.run(
            [str(helper_path), "window_info"],
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
def check_helper_dir() -> bool:
    """Checks for the window helper executable."""
    helper_path = get_helper_path()
    print(f"[DEBUG] Looking for `window_helper` at: {helper_path}")
    path_exists = helper_path.exists()
    print(f"[DEBUG] {"Found" if path_exists else "Missing"} `window_helper` executable.")
    return path_exists

def test_window_helper(verbose: bool = True) -> bool:
    # TODO: Fix the issue of this function hanging when called in a frozen environment.
    """
    Tests whether the window_helper executable is available and working.
    Returns True if successful, False otherwise.
    """
    helper_path = get_helper_path()
    if not helper_path.exists():
        if verbose:
            print(f"❌ Helper not found at: {helper_path}")
        return False

    try:
        result = subprocess.run(
            [str(helper_path), "window_info"],
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
    test_window_helper()