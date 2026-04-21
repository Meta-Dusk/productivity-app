"""
Window detection helper script. Run `build_helper.bat` to build.
"""
import json, sys, psutil, pythoncom, signal
import uiautomation as auto

def get_active_window_info():
    try:
        ctrl = auto.GetForegroundControl()
        if ctrl is None:
            return {"name": None, "class_name": None, "pid": 0, "process_name": None}
        
        pid: int = getattr(ctrl, "ProcessId", 0)
        process_name: str = None
        if pid:
            try:
                process_name = psutil.Process(pid).name()
            except Exception:
                process_name = "unknown"
                
        return {
            "name": getattr(ctrl, "Name", None),
            "class_name": getattr(ctrl, "ClassName", None),
            "pid": pid,
            "process_name": process_name
        }
    except Exception as e:
        return {"error": str(e), "name": None, "class_name": None, "pid": 0, "process_name": None}

def handle_sigterm(*_):
    """Exit gracefully when terminated by parent process."""
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_sigterm)


if __name__ == "__main__":
    pythoncom.CoInitialize()
    try:
        while True:
            command = sys.stdin.readline()
            if not command: break  # Pipe closed (EOF)
            command = command.strip()

            if command == "get_window_info":
                info = get_active_window_info()
                sys.stdout.write(json.dumps(info) + "\n")
                sys.stdout.flush()
            elif command == "exit":
                break
            else:
                sys.stdout.write(json.dumps({"error": "Invalid command"}) + "\n")
                sys.stdout.flush()
    finally:
        pythoncom.CoUninitialize()