import copy

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)
ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


def reset_activities_state():
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


@pytest.fixture(autouse=True)
def reset_activities():
    reset_activities_state()
    yield
    reset_activities_state()


def test_get_activities_returns_activity_list():
    # Arrange: initial state is prepared by fixture
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)
    assert data["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_participant_success():
    # Arrange
    activity_name = "Chess Club"
    participant_email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": participant_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {participant_email} for {activity_name}"
    assert participant_email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = "Chess Club"
    participant_email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": participant_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_success():
    # Arrange
    activity_name = "Chess Club"
    participant_email = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": participant_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {participant_email} from {activity_name}"
    assert participant_email not in activities[activity_name]["participants"]


def test_remove_nonexistent_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    participant_email = "ghost@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": participant_email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
