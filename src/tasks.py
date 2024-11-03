from flask import Flask, request
import sqlite3
import functools
import uuid
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from .keys import api_required
from .db import get_db

bp = Blueprint("tasks", __name__, url_prefix="/tasks")

ok = {"message": "ok"}, 200

@dataclass
class Task:
    name: str
    startDate: int
    status: str


def list_tasks() -> List[Task]:
    conn = get_db()
    cursor = conn.cursor()
    x = cursor.execute(
        """
        SELECT *
        FROM task
        """
    ).fetchall()
    return [Task(*row) for row in x]


def get_task(name: str) -> Task:
    conn = get_db()
    cursor = conn.cursor()
    row = cursor.execute(
        """
        SELECT *
        FROM task
        Where name = :name
        """,
        {"name": name},
    ).fetchone()
    if row is not None:
        return Task(*row)
    else:
        return None


def add_task(name: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO task (name)
        VALUES (:name)
        """,
        {"name": name},
    )
    conn.commit()


def delete_task(name: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        DELETE FROM task
        WHERE name = :name
        """,
        {"name": name},
    )
    conn.commit()


def update_task(task: Task):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE task
        SET startDate = :startDate,
            status = :status
        WHERE name = :name
        """,
        asdict(task),
    )
    conn.commit()


@bp.route("/", methods=["GET"])
@api_required
def tasks_get():
    return {"tasks": list_tasks()}, 200


@bp.route("/", methods=["POST"])
@api_required
def tasks_post():
    name = request.json.get("name")
    task = get_task(name)
    if task is not None:
        return {"message": "Task with this name already exists."}, 500
    add_task(name)
    return ok


@bp.route("/", methods=["DELETE"])
@api_required
def tasks_delete():
    name = request.json.get("name")
    task = get_task(name)
    if task is None:
        return {"message": "Task not found."}, 500
    delete_task(name)
    return ok


@bp.route("/start", methods=["PUT"])
@api_required
def tasks_start_put():
    name = request.json.get("name")
    task = get_task(name)
    if task is None:
        return {"message": "Task not found."}, 500
    if task.status != "Created":
        return {"message": "Task was already started."}, 500

    task.status = "Running"
    task.startDate = str(datetime.today())
    update_task(task)
    return ok


@bp.route("/stop", methods=["PUT"])
@api_required
def tasks_stop_put():
    name = request.json.get("name")
    task = get_task(name)
    if task is None:
        return {"message": "Task not found."}, 500
    if task.status != "Running":
        return {"message": "Task isn't running."}, 500

    task.status = "Failed"
    update_task(task)
    return ok


@bp.route("/finish", methods=["PUT"])
@api_required
def tasks_finish_put():
    name = request.json.get("name")
    if task is None:
        return {"message": "Task not found."}, 500
    if task.status != "Running":
        return {"message": "Task isn't running."}, 500

    task.status = "Successful"
    update_task(task)
    return ok