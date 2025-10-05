from enum import Enum

class AppType(Enum):
    DISTRACTING = "distracting"
    NEUTRAL = "neutral"
    PRODUCTIVE = "productive"

class WindowInfo(Enum):
    NAME = "name"
    CLASS_NAME = "class_name"
    PROCESS_ID = "process_id"