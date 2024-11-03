import functools

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import request
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from flask import Flask, request
import sqlite3
import functools
import uuid
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List

from .db import get_db

bp = Blueprint("keys", __name__, url_prefix="/keys")

ok = {"message": "ok"}, 200


def is_valid(api_key: str):
    conn = get_db()
    key_valid = (
        conn.cursor()
        .execute(
            "Select exists(Select * from apiKey where active = 1 and key = :key)",
            {"key": api_key},
        )
        .fetchone()[0]
    )
    return key_valid == 1


def add_key(api_key: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR IGNORE INTO apiKey (key)
        VALUES (:key)
        """,
        {"key": api_key},
    )
    conn.commit()
    conn.close()


def delete_key(api_key: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        DELETE FROM apiKey
        WHERE key = :key
        """,
        {"key": api_key},
    )
    conn.commit()
    conn.close()


def set_key_status(api_key: str, active: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE apiKey
        SET active = :active
        WHERE key = :key
        """,
        {"active": active, "key": api_key},
    )
    conn.commit()
    conn.close()


def api_required(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        if request.json:
            api_key = request.json.get("api_key")
        else:
            return {"message": "Please provide an API key"}, 401
        # Check if API key is correct and valid
        if is_valid(api_key):
            return func(*args, **kwargs)
        else:
            return {"message": "The provided API key is not valid"}, 403

    return decorator


@bp.route("/new", methods=["POST"])
@api_required
def route_make_key():
    key = str(uuid.uuid4())
    add_key(key)
    return {"new_key": key}, 200


@bp.route("/", methods=["DELETE"])
@api_required
def route_delete_key():
    key = request.json.get("key")
    delete_key(key)
    return ok


@bp.route("/activate", methods=["PUT"])
@api_required
def route_activate_key():
    key = request.json.get("key")
    set_key_status(key, 1)
    return ok


@bp.route("/deactivate", methods=["PUT"])
@api_required
def route_deactivate_key():
    key = request.json.get("key")
    set_key_status(key, 0)
    return ok
