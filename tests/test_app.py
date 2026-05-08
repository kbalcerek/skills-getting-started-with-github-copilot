
import copy
import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient
import src.app
from src.app import app


@pytest.fixture(autouse=True)
def restore_activities():
    """Snapshot and restore the global activities state around each test."""
    original = copy.deepcopy(src.app.activities)
    yield
    src.app.activities.clear()
    src.app.activities.update(original)


async def test_get_activities():
    # Arrange
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Act
        response = await ac.get("/activities")
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

async def test_signup_for_activity_success():
    # Arrange
    test_email = "testuser@mergington.edu"
    activity = "Chess Club"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Act
        response = await ac.post(f"/activities/{activity}/signup?email={test_email}")
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert f"Signed up {test_email} for {activity}" in response.json().get("message", "")

async def test_signup_for_activity_already_signed_up():
    # Arrange
    existing_email = "michael@mergington.edu"
    activity = "Chess Club"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Act
        response = await ac.post(f"/activities/{activity}/signup?email={existing_email}")
    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Student already signed up"

async def test_signup_for_activity_not_found():
    # Arrange
    test_email = "testuser@mergington.edu"
    activity = "Nonexistent Club"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Act
        response = await ac.post(f"/activities/{activity}/signup?email={test_email}")
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Activity not found"

async def test_unregister_from_activity_success():
    # Arrange
    test_email = "michael@mergington.edu"
    activity = "Chess Club"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Act
        response = await ac.delete(f"/activities/{activity}/signup?email={test_email}")
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert f"Removed {test_email} from {activity}" in response.json().get("message", "")

async def test_unregister_from_activity_not_signed_up():
    # Arrange
    test_email = "not_signed_up@mergington.edu"
    activity = "Chess Club"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Act
        response = await ac.delete(f"/activities/{activity}/signup?email={test_email}")
    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Student not signed up"

async def test_unregister_from_activity_not_found():
    # Arrange
    test_email = "testuser@mergington.edu"
    activity = "Nonexistent Club"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Act
        response = await ac.delete(f"/activities/{activity}/signup?email={test_email}")
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Activity not found"
