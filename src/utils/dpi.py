"""DPI setup is intentionally called once by run_aegis, never on import."""
from __future__ import annotations
import ctypes

def init_dpi_awareness() -> bool:
    if not hasattr(ctypes, "windll"):
        return False
    try:
        if ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4)):
            return True
    except (AttributeError, OSError):
        pass
    try:
        if ctypes.windll.shcore.SetProcessDpiAwareness(2) == 0:
            return True
    except (AttributeError, OSError):
        pass
    try:
        return bool(ctypes.windll.user32.SetProcessDPIAware())
    except (AttributeError, OSError):
        return False
