from flask import Flask, jsonify, request, abort
import json
import os
from datetime import datetime

app = Flask(__name__)

# File to store courses data
COURSES_FILE = 'courses.json'

# Allowed status values
ALLOWED_STATUS = ["Not Started", "In Progress", "Completed"]


def initialize_courses_file():
    """
    Create the courses.json file if it doesn't exist.
    Initializes with an empty list.
    """
    if not os.path.exists(COURSES_FILE):
        try:
            with open(COURSES_FILE, 'w') as f:
                json.dump([], f)
        except IOError:
            print("Error creating courses.json file.")


def read_courses():
    """
    Reads the list of courses from the JSON file.
    Returns an empty list if file is empty or not exists.
    """
    try:
        with open(COURSES_FILE, 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        # If reading fails, return empty list to avoid crashes
        return []


def write_courses(courses):
    """
    Writes the list of courses back to the JSON file.
    Raises IOError if write fails.
    """
    with open(COURSES_FILE, 'w') as f:
        json.dump(courses, f, indent=4)


def get_next_id(courses):
    """
    Helper to get the next available course ID.
    """
    if courses:
        # max existing id + 1
        return max(course['id'] for course in courses) + 1
    else:
        return 1


def validate_date(date_str):
    """
    Validates date format YYYY-MM-DD.
    Returns True if valid, False otherwise.
    """
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_course_data(data, require_all_fields=True):
    """
    Validates input course data.
    Checks for required fields and correct status and date formats.
    If require_all_fields is False, allows partial updates.
    Returns (is_valid, error_message) tuple.
    """
    required_fields = ['name', 'description', 'target_date', 'status']
    
    # Check for required fields in POST (create) or PUT (update with require_all_fields=True)
    if require_all_fields:
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: '{field}'"
    else:
        # For partial PUT updates, no need to have all fields
        if not any(field in data for field in required_fields):
            return False, f"At least one of the fields {required_fields} must be provided for update."
    
    # Validate status if provided
    if 'status' in data and data['status'] not in ALLOWED_STATUS:
        return False, f"Invalid status value. Allowed values are: {ALLOWED_STATUS}"
    
    # Validate date format if provided
    if 'target_date' in data and not validate_date(data['target_date']):
        return False, "Invalid target_date format. Use 'YYYY-MM-DD'."
    
    return True, None


@app.route('/api/courses', methods=['POST'])
def create_course():
    """
    Create/add a new course.
    Expects JSON body with name, description, target_date, status.
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request must be JSON"}), 400
    
    # Validate input fields for course creation
    valid, error_msg = validate_course_data(data, require_all_fields=True)
    if not valid:
        return jsonify({"error": error_msg}), 400
    
    courses = read_courses()
    
    # Generate new ID
    new_id = get_next_id(courses)
    
    # Current timestamp ISO format
    created_at = datetime.utcnow().isoformat() + 'Z'  # Append Z for UTC
    
    course = {
        "id": new_id,
        "name": data['name'].strip(),
        "description": data['description'].strip(),
        "target_date": data['target_date'],
        "status": data['status'],
        "created_at": created_at
    }
    
    courses.append(course)
    try:
        write_courses(courses)
    except IOError:
        return jsonify({"error": "Failed to write to courses.json"}), 500
    
    return jsonify(course), 201


@app.route('/api/courses', methods=['GET'])
def get_all_courses():
    """
    Get list of all courses.
    """
    courses = read_courses()
    return jsonify(courses)


@app.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    """
    Get a specific course by its ID.
    """
    courses = read_courses()
    course = next((c for c in courses if c['id'] == course_id), None)
    
    if course is None:
        return jsonify({"error": "Course not found"}), 404
    
    return jsonify(course)


@app.route('/api/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    """
    Update an existing course.
    Allows partial updates (not all fields required).
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Request must be JSON"}), 400
    
    # Validate input; partial fields allowed
    valid, error_msg = validate_course_data(data, require_all_fields=False)
    if not valid:
        return jsonify({"error": error_msg}), 400
    
    courses = read_courses()
    course = next((c for c in courses if c['id'] == course_id), None)
    
    if course is None:
        return jsonify({"error": "Course not found"}), 404
    
    # Update fields if present in request data
    if 'name' in data:
        course['name'] = data['name'].strip()
    if 'description' in data:
        course['description'] = data['description'].strip()
    if 'target_date' in data:
        course['target_date'] = data['target_date']
    if 'status' in data:
        course['status'] = data['status']
    
    try:
        write_courses(courses)
    except IOError:
        return jsonify({"error": "Failed to write to courses.json"}), 500
    
    return jsonify(course)


@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    """
    Delete a course by its ID.
    """
    courses = read_courses()
    course = next((c for c in courses if c['id'] == course_id), None)
    
    if course is None:
        return jsonify({"error": "Course not found"}), 404
    
    # Remove the course
    courses = [c for c in courses if c['id'] != course_id]
    
    try:
        write_courses(courses)
    except IOError:
        return jsonify({"error": "Failed to write to courses.json"}), 500
    
    return jsonify({"message": f"Course with id {course_id} deleted."}), 200


if __name__ == '__main__':
    # Ensure the courses.json file exists before starting
    initialize_courses_file()
    
    # Run the Flask app on port 5000 (default) with debug mode on for development
    app.run(debug=True)