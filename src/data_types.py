from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class AppType(Enum):
    DISTRACTING = "distracting"
    NEUTRAL = "neutral"
    PRODUCTIVE = "productive"

class WindowInfo(Enum):
    NAME = "name"
    CLASS_NAME = "class_name"
    PROCESS_ID = "process_id"
    
@dataclass
class Productive:
    apps: Optional[list[str]] = field(default_factory=list)
    keywords: Optional[list[str]] = field(default_factory=list)

@dataclass
class Distracting:
    apps: Optional[list[str]] = field(default_factory=list)
    keywords: Optional[list[str]] = field(default_factory=list)

@dataclass
class WindowNames:
    productive: Productive = field(default_factory=Productive)
    distracting: Distracting = field(default_factory=Distracting)