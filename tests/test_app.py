import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app
import src.app as app_module

client = TestClient(app)
original_activities = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activity_state():
    app_module.activities = copy.deepcopy(original_activities)
    yield


def test_get_activities_returns_all_activities():
    # Arrange
    expected_activity_name = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert expected_activity_name in activities
    assert activities[expected_activity_name]["description"] == "Learn strategies and compete in chess tournaments"
    assert "michael@mergington.edu" in activities[expected_activity_name]["participants"]


def test_signup_participant_adds_new_email():
    # Arrange
    activity_name = "Chess Club"
    new_email = "alex@mergington.edu"
    signup_url = f"/activities/{activity_name}/signup?email={new_email}"

    # Act
    response = client.post(signup_url)

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == f"Signed up {new_email} for {activity_name}"
    assert new_email in app_module.activities[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"
    signup_url = f"/activities/{activity_name}/signup?email={existing_email}"

    # Act
    response = client.post(signup_url)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_delete_participant_removes_participant():
    # Arrange
    activity_name = "Chess Club"
    email_to_remove = "daniel@mergington.edu"
    delete_url = f"/activities/{activity_name}/participants?email={email_to_remove}"

    # Act
    response = client.delete(delete_url)

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == f"Removed {email_to_remove} from {activity_name}"
    assert email_to_remove not in app_module.activities[activity_name]["participants"]


def test_delete_nonexistent_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    missing_email = "missing.student@mergington.edu"
    delete_url = f"/activities/{activity_name}/participants?email={missing_email}"

    # Act
    response = client.delete(delete_url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
