import psutil, pythoncom
import uiautomation as auto

from typing import Optional
from data_types import WindowInfo, AppType, WindowNames


def get_active_window_info() -> dict[WindowInfo, Optional[str | int]]:
    """Returns dict with info about the currently focused window."""
    try:
        # Explicitly initialize COM for the thread
        pythoncom.CoInitialize()

        with auto.UIAutomationInitializerInThread():
            ctrl = auto.GetForegroundControl()
            if ctrl is None:
                return {
                    WindowInfo.NAME: None,
                    WindowInfo.CLASS_NAME: None,
                    WindowInfo.PROCESS_ID: 0,
                }
            return {
                WindowInfo.NAME: getattr(ctrl, "Name", None),
                WindowInfo.CLASS_NAME: getattr(ctrl, "ClassName", None),
                WindowInfo.PROCESS_ID: getattr(ctrl, "ProcessId", 0),
            }

    except Exception as e:
        # Catch catastrophic COM failures or unexpected automation errors
        print(f"⚠️ UIAutomation error: {e}")
        return {
            WindowInfo.NAME: None,
            WindowInfo.CLASS_NAME: None,
            WindowInfo.PROCESS_ID: 0,
        }

    finally:
        # Always uninitialize COM to avoid leaks
        try:
            pythoncom.CoUninitialize()
        except:
            pass

def get_process_name(pid: int) -> str:
    try:
        return psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, ValueError):
        return "unknown"
