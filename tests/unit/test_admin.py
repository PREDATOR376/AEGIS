import pytest
from src.utils.admin import is_admin, require_admin

def test_is_admin_returns_bool():
    assert isinstance(is_admin(), bool)

def test_require_admin_has_actionable_error(monkeypatch):
    monkeypatch.setattr("src.utils.admin.is_admin", lambda: False)
    with pytest.raises(PermissionError, match="Run as Administrator"):
        require_admin("DXGI")
