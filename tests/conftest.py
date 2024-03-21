import pytest

from scheduler.schedule import TV


@pytest.fixture(scope="function")
def off_tv():
    return TV()
