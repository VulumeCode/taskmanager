

from flask import Flask, send_from_directory, request, g
from os import sys
import re
import sqlite3
import functools
import uuid
from typing import List
DATABASE = 'database.db'

app = Flask(__name__)


def ok(): return {"message":"ok"}, 300

def create_table():
    # Connect to the SQLite database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task (
            name TEXT PRIMARY KEY,
            startDate INTEGER DEFAULT NULL,
            status TEXT DEFAULT 'Created'
        )''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS apiKey (
            key TEXT PRIMARY KEY,
            active INTEGER DEFAULT 1 NOT NULL
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

@app.before_first_request
def initialize_database():
    # Call the create_table function before handling the first request
    create_table()
    add_key("admin")

def is_valid(api_key: str):
    conn = sqlite3.connect(DATABASE)
    key_valid = conn.cursor().execute("Select exists(Select * from apiKey where active = 1 and key = :key)", {"key": api_key}).fetchone()[0]
    return key_valid == 1

def add_key(api_key: str):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO apiKey (key)
        VALUES (:key)
        ''', {"key": api_key})
    conn.commit()
    conn.close()

def delete_key(api_key: str):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM apiKey
        WHERE key = :key
        ''', {"key": api_key})
    conn.commit()
    conn.close()

def set_key_status(api_key: str, active: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE apiKey
        SET active = :active
        WHERE key = :key
        ''', {"active": active, "key": api_key})
    conn.commit()
    conn.close()


def api_required(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        if request.json:
            api_key = request.json.get("api_key")
        else:
            return {"message": "Please provide an API key"}, 400
        # Check if API key is correct and valid
        if is_valid(api_key):
            return func(*args, **kwargs)
        else:
            return {"message": "The provided API key is not valid"}, 403
    return decorator

@app.route('/keys/new', methods=['POST'])
@api_required
def make_key():
    key = str(uuid.uuid4())
    add_key(key)
    return {"new_key":key}, 300

@app.route('/keys', methods=['DELETE'])
@api_required
def delete_key():
    key = request.json.get("key")
    delete_key(key)
    return ok()

@app.route('/keys/activate', methods=['PUT'])
@api_required
def activate_key():
    key = request.json.get("key")
    set_key_status(key, 1)
    return ok()

@app.route('/keys/deactivate', methods=['PUT'])
@api_required
def deactivate_key():
    key = request.json.get("key")
    set_key_status(key, 0)
    return ok()




### tasks
class Task:
    def __init__(name: str, startDate: int, status: str):
        self.name = name 
        self.startDate = startDate 
        self.status = status 

    # def json():
    #     return {
    #         "name": self.name , 
    #         "startDate": self.startDate , 
    #         "status": self.status , 
    #     }


def list_tasks() -> List[Task]:
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT *
        FROM task
        ''')
    
    result = list(map(lambda row: Task(*row), cursor))
    conn.commit()
    conn.close()
    return result

def add_task(name: str):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO task (name)
        VALUES (:name)
        ''', {"name": name})
    conn.commit()
    conn.close()

@app.route('/tasks', methods=['GET'])
@api_required
def tasks_get():
    return {
        "tasks": list_tasks()
    }, 300

@app.route('/tasks', methods=['POST'])
@api_required
def tasks_post():
    name = request.json.get("name")
    add_task(name)
    return ok()
