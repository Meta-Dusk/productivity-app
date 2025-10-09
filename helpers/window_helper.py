"""
Window detection helper script. Build this then put the executable in ./src/bin/.
Build with:
`pyinstaller --onefile --noconsole helpers/window_helper.py`
"""
import json, sys, psutil, pythoncom, signal
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


def handle_sigterm(*_):
    """Exit gracefully when terminated by parent process."""
    sys.exit(0)


signal.signal(signal.SIGTERM, handle_sigterm)


if __name__ == "__main__":
    while True:
        try:
            command = sys.stdin.readline()
            if not command:
                break  # Pipe closed (EOF)
            command = command.strip()

            if command == "get_window_info":
                info = get_active_window_info()
                if info.get("pid"):
                    info["process_name"] = get_process_name(info["pid"])
                sys.stdout.write(json.dumps(info) + "\n")
                sys.stdout.flush()
            elif command == "exit":
                break
            else:
                sys.stdout.write(json.dumps({"error": "Invalid command"}) + "\n")
                sys.stdout.flush()

        except (OSError, ValueError) as e:
            # Exit quietly if stdout or stdin is closed
            if hasattr(e, "errno") and e.errno == 22:
                break
            break
        except Exception:
            break
