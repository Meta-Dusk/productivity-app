import psutil
import uiautomation as auto

from typing import Optional
from data_types import WindowInfo, AppType


def get_active_window_info() -> dict[WindowInfo, Optional[str | int]]:
    """Returns dict with info about the currently focused window."""
    # Proper COM init for this thread
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

def get_process_name(pid: int) -> str:
    try:
        return psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, ValueError):
        return "unknown"

def classify_window(
    win_info: dict[WindowInfo, Optional[str | int]],
    app_list: list,
    keywords: list
) -> AppType:
    title = (win_info.get(WindowInfo.NAME) or "").lower()
    process = (get_process_name(win_info.get(WindowInfo.PROCESS_ID)) or "").lower()
    
    if any(app.lower() in process for app in app_list):
        return AppType.PRODUCTIVE
    elif any(word.lower() in title for word in keywords):
        return AppType.DISTRACTING
    else:
        return AppType.NEUTRAL