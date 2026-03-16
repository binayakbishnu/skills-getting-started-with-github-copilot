import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to clean state before and after each test"""
    original_activities = copy.deepcopy(activities)
    yield
    # Restore after test
    activities.clear()
    activities.update(original_activities)
