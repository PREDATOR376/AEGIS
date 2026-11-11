import pytest

def pytest_addoption(parser):
    parser.addoption("--live", action="store_true", help="run tests that require GTA V and an elevated terminal")

def pytest_configure(config):
    config.addinivalue_line("markers", "live: requires GTA V running and Administrator privileges")

def pytest_collection_modifyitems(config, items):
    if not config.getoption("--live"):
        marker = pytest.mark.skip(reason="Need --live and GTA V running")
        for item in items:
            if "live" in item.keywords:
                item.add_marker(marker)
