

from flask import Flask, send_from_directory, request, g
from os import sys
import re
import sqlite3
import functools


DATABASE = 'database.db'

app = Flask(__name__)

def create_table():
    # Connect to the SQLite database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task (
            name TEXT PRIMARY KEY,
            startDate INTEGER,
            status TEXT NOT NULL
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

def is_valid(api_key):
    print(api_key)
    conn = sqlite3.connect(DATABASE)
    key_valid = conn.cursor().execute("Select exists(Select * from apiKey where active = 1 and key = :key)", {"key": api_key}).fetchone()
    return key_valid is not None


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

@app.route('/tasks', methods=['GET'])
@api_required
def tasks_get():
    conn = sqlite3.connect(DATABASE)
    return "ok"
