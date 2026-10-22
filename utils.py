import json
from threading import Lock

FILE_PATH = 'courses.json'
lock = Lock()

def read_courses():
    with lock:
        try:
            with open(FILE_PATH, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

def write_courses(courses):
    with lock:
        with open(FILE_PATH, 'w') as f:
            json.dump(courses, f, indent=2)