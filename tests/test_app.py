import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture(autouse=True)
def client():
    # Preserve the original in-memory activities and restore after each test
    original = copy.deepcopy(app_module.activities)
    client = TestClient(app_module.app)
    yield client
    # Restore original state
    app_module.activities.clear()
    app_module.activities.update(original)


def test_get_activities(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_duplicate_and_unregister(client):
    activity = "Chess Club"
    email = "tester@example.com"

    # Signup should succeed
    resp = client.post(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Duplicate signup should fail
    resp2 = client.post(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    assert resp2.status_code == 400

    # Participant should be present
    resp3 = client.get("/activities")
    assert email in resp3.json()[activity]["participants"]

    # Unregister participant
    resp4 = client.delete(f"/activities/{quote(activity)}/participants?email={quote(email)}")
    assert resp4.status_code == 200
    assert "Unregistered" in resp4.json().get("message", "")

    # Ensure participant removed
    resp5 = client.get("/activities")
    assert email not in resp5.json()[activity]["participants"]
