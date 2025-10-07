"""
Window detection helper script. Build this then put the executable in ./src/bin/.
Build with:
`pyinstaller --onefile --noconsole helpers/window_helper.py`
"""
import json, sys, psutil, pythoncom
import uiautomation as auto


def get_active_window_info():
    try:
        pythoncom.CoInitialize()
        with auto.UIAutomationInitializerInThread():
            ctrl = auto.GetForegroundControl()
            if ctrl is None:
                return {"name": None, "class_name": None, "pid": 0}
            return {
                "name": getattr(ctrl, "Name", None),
                "class_name": getattr(ctrl, "ClassName", None),
                "pid": getattr(ctrl, "ProcessId", 0),
            }
    except Exception as e:
        return {"error": str(e), "name": None, "class_name": None, "pid": 0}
    finally:
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass


def get_process_name(pid):
    try:
        return psutil.Process(pid).name()
    except Exception:
        return "unknown"


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "window_info":
        info = get_active_window_info()
        if info["pid"]:
            info["process_name"] = get_process_name(info["pid"])
        print(json.dumps(info))
    else:
        print(json.dumps({"error": "Invalid command"}))
