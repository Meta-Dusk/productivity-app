"""
Quick test for WindowHelperManager lifecycle.
Ensures the helper subprocess starts, retrieves data, and exits cleanly.
"""
import time
from managers.window import WindowHelperManager


def test() -> None:
    print("🚀 Starting WindowHelperManager test...")

    manager = WindowHelperManager()
    if not manager.check_path():
        print("❌ window_helper.exe not found. Make sure it's built and placed in ./assets/bin/")
        return

    if not manager.start():
        print(f"❌ Failed to start helper: {manager.error}")
        return

    print("✅ Helper started successfully. Fetching data for 5 seconds...")
    start_time = time.time()

    while time.time() - start_time < 5:
        data = manager.get_latest_window_info()
        print(f"🪟 Active window: {data}")
        time.sleep(1)

    print("🧹 Stopping helper...")
    manager.stop()

    if manager.error:
        print(f"⚠️ Error detected: {manager.error}")
    else:
        print("✅ Helper stopped cleanly. No exceptions should appear.")

    print("🎉 Test complete! You can close this window safely.")


if __name__ == "__main__":
    test()