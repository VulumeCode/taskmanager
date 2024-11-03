import pytest
import json

import taskmanager.tasks as tasks

testTaskName = "doit"


def test_get_all(client):
    response = client.get(
        "/tasks/",
        json={"api_key": "admin"},
    )
    assert response.status_code == 200
    tasks = json.loads(response.data)["tasks"]
    assert len(tasks) == 1
    assert tasks[0]["name"] == testTaskName


def test_post(app, client):
    newTaskName = "a task"

    assert (
        client.post(
            "/tasks/",
            json={"api_key": "admin", "name": newTaskName},
        ).status_code
        == 200
    )

    with app.app_context():
        theTasks = tasks.list_tasks()
        assert len(theTasks) == 2
        assert tasks.list_tasks()[1].name == newTaskName


def test_delete(app, client):
    assert (
        client.delete(
            "/tasks/",
            json={"api_key": "admin", "name": testTaskName},
        ).status_code
        == 200
    )

    with app.app_context():
        theTasks = tasks.list_tasks()
        assert len(theTasks) == 0


def test_start(app, client):
    assert (
        client.put(
            "/tasks/start",
            json={"api_key": "admin", "name": testTaskName},
        ).status_code
        == 200
    )

    with app.app_context():
        theTask = tasks.list_tasks()[0]
        assert theTask.startDate != None
        assert theTask.status == "Running"


def test_start_error_notfound(app, client):
    testTaskNameError = "notfound"

    assert (
        client.put(
            "/tasks/start",
            json={"api_key": "admin", "name": testTaskNameError},
        ).status_code
        == 404
    )


def test_start_error_already_started(app, client):
    assert (
        client.put(
            "/tasks/start",
            json={"api_key": "admin", "name": testTaskName},
        ).status_code
        == 200
    )

    assert (
        client.put(
            "/tasks/start",
            json={"api_key": "admin", "name": testTaskName},
        ).status_code
        == 500
    )


def test_stop(app, client):
    assert (
        client.put(
            "/tasks/start",
            json={"api_key": "admin", "name": testTaskName},
        ).status_code
        == 200
    )
    assert (
        client.put(
            "/tasks/stop",
            json={"api_key": "admin", "name": testTaskName},
        ).status_code
        == 200
    )

    with app.app_context():
        theTask = tasks.list_tasks()[0]
        assert theTask.startDate != None
        assert theTask.status == "Failed"


def test_finish(app, client):
    assert (
        client.put(
            "/tasks/start",
            json={"api_key": "admin", "name": testTaskName},
        ).status_code
        == 200
    )
    assert (
        client.put(
            "/tasks/finish",
            json={"api_key": "admin", "name": testTaskName},
        ).status_code
        == 200
    )

    with app.app_context():
        theTask = tasks.list_tasks()[0]
        assert theTask.startDate != None
        assert theTask.status == "Successful"

