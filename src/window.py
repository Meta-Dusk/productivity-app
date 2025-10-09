import json, subprocess, sys, threading, queue, time
from pathlib import Path
from typing import Optional, Dict
from data_types import WindowInfo


# === SUBPROCESS MANAGER ===
class WindowHelperManager:
    """Manages a persistent subprocess for fetching window info."""
    def __init__(self):
        self.helper_path = self._get_helper_path()
        self.process = None
        self.data_queue = queue.Queue()  # Thread-safe queue for latest data
        self.running = False
        self.thread = None
        self.latest_data = {
            WindowInfo.NAME: None,
            WindowInfo.CLASS_NAME: None,
            WindowInfo.PROCESS_ID: 0,
        }
        self.error = None
        
    def _get_helper_path(self) -> Path:
        """Returns the correct path even when used in a built executable."""
        if getattr(sys, "frozen", False):
            base_dir = Path(sys.executable).resolve().parent
        else:
            base_dir = Path(__file__).resolve().parent
        return base_dir / "assets" / "bin" / "window_helper.exe"
    
    def check_path(self) -> bool:
        """Checks if the path of the built executable exists."""
        if self._get_helper_path().exists():
            return True
        return False
    
    def start(self) -> bool:
        """Initialize the `WindowManagerHelper`."""
        if not self.helper_path.exists():
            self.error = f"Helper executable not found: {self.helper_path}"
            print(f"⚠️ {self.error}")
            return False

        try:
            self.process = subprocess.Popen(
                [str(self.helper_path)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line-buffered
            )
            self.running = True
            self.thread = threading.Thread(target=self._monitor_loop)
            self.thread.daemon = True
            self.thread.start()
            return True
        except Exception as e:
            self.error = f"Failed to start helper: {e}"
            print(f"⚠️ {self.error}")
            return False

    def _monitor_loop(self):
        """Handles the data expected from the window_helper subprocess."""
        while self.running:
            try:
                self.process.stdin.write("get_window_info\n")
                self.process.stdin.flush()
                output = self.process.stdout.readline().strip()
                if output:
                    data = json.loads(output)
                    self.latest_data = {
                        WindowInfo.NAME: data.get("name"),
                        WindowInfo.CLASS_NAME: data.get("class_name"),
                        WindowInfo.PROCESS_ID: data.get("pid"),
                    }
                    self.data_queue.put(self.latest_data)
            except Exception as e:
                self.error = str(e)
                print(f"⚠️ Helper error: {e}")
                break
            time.sleep(1)  # Fetch every second

        # Cleanup on exit
        if self.process:
            self.process.stdin.write("exit\n")
            self.process.stdin.flush()
            self.process.terminate()
            self.process.wait(timeout=5)

    def get_latest_window_info(self) -> Dict[WindowInfo, Optional[str | int]]:
        """Get the most recent window info without blocking."""
        try:
            while not self.data_queue.empty():
                self.latest_data = self.data_queue.get_nowait()
        except queue.Empty:
            pass
        return self.latest_data if not self.error else {
            WindowInfo.NAME: None,
            WindowInfo.CLASS_NAME: None,
            WindowInfo.PROCESS_ID: 0,
        }

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)


# === MAIN FUNCTIONS ===
# Note: get_active_window_info() is now replaced by .get_latest_window_info()
# Initialize the manager once in your app, e.g., in main()

def get_process_name(process_id: int) -> str:
    """We already include process name in the helper output."""
    return "N/A"  # (kept for interface compatibility)


# === TESTERS ===
def check_helper_dir() -> bool:
    """Checks for the window helper executable."""
    manager = WindowHelperManager()
    helper_path = manager._get_helper_path()
    print(f"[DEBUG] 🔎 Looking for `window_helper` at: {helper_path}")
    path_exists = helper_path.exists()
    print(f"[DEBUG] ✅ {"Found" if path_exists else "Missing"} `window_helper` executable.")
    return path_exists

def test_window_helper(verbose: bool = True) -> bool:
    """
    Tests whether the window_helper is available and working in persistent mode.
    Returns True if successful, False otherwise.
    """
    manager = WindowHelperManager()
    if not manager._get_helper_path().exists():
        if verbose:
            print(f"❌ Helper not found at: {manager.helper_path}")
        return False

    manager.start()
    if manager.error:
        if verbose:
            print(f"❌ {manager.error}")
        manager.stop()
        return False

    # Wait a bit for first data
    time.sleep(2)  # Allow time for initial fetch

    data = manager.get_latest_window_info()
    expected_keys = {WindowInfo.NAME, WindowInfo.CLASS_NAME, WindowInfo.PROCESS_ID}

    if not all(key in data for key in expected_keys):
        if verbose:
            print(f"⚠️ Invalid helper output: {data}")
        manager.stop()
        return False

    if verbose:
        print("✅ Helper test passed.")
        print(f"Active window: {data.get(WindowInfo.NAME)} (PID: {data.get(WindowInfo.PROCESS_ID)})")

    manager.stop()
    return True

# Run this file to test if the helper works.
if __name__ == "__main__":
    test_window_helper()