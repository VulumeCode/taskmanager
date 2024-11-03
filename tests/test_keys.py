import pytest
import json


def test_no_key(client):
    assert (
        client.put(
            "/tasks/start",
            json={},
        ).status_code
        == 401
    )


def test_invalid_key(client):
    assert (
        client.put(
            "/tasks/start",
            json={"api_key": "wrong"},
        ).status_code
        == 403
    )


def test_inactive_key(client):
    assert (
        client.put(
            "/keys/deactivate",
            json={"api_key": "admin", "key": "admin"},
        ).status_code
        == 200
    )
    assert (
        client.put(
            "/tasks/start",
            json={"api_key": "admin"},
        ).status_code
        == 403
    )


def test_delete_key(client):
    assert (
        client.delete(
            "/keys/",
            json={"api_key": "admin", "key": "admin"},
        ).status_code
        == 200
    )
    assert (
        client.put(
            "/tasks/start",
            json={"api_key": "admin"},
        ).status_code
        == 403
    )


def test_new_key(client):
    response = client.post(
        "/keys/new",
        json={"api_key": "admin"},
    )
    assert response.status_code == 200
    newKey = json.loads(response.data)["new_key"]

    assert (
        client.get(
            "/tasks/",
            json={"api_key": newKey},
        ).status_code
        == 200
    )
