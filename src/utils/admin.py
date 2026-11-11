from __future__ import annotations
import ctypes

def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except (AttributeError, OSError):
        return False

def require_admin(reason: str) -> None:
    if not is_admin():
        raise PermissionError(f"AEGIS requires Administrator privileges for {reason}. Right-click your terminal and choose 'Run as Administrator'.")
