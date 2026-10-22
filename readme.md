# CodeCraftHub Course API

A Flask API for creating courses and tracking their progress. Data is stored locally in `courses.json`.

## Start the API

Run these commands from the project folder with Python installed:

```powershell
python -m pip install Flask
python app.py
```

Leave the server running and open a second terminal for the requests below. The development server runs at http://localhost:5000. Press `Ctrl+C` in its terminal to stop it. Debug mode is for local development only.

## API Examples

These commands use PowerShell and `curl.exe` to avoid PowerShell's `curl` alias. The `-i` option includes the HTTP status and headers in the response. JSON bodies are piped through standard input to avoid Windows command-line quoting issues.

Creating, updating, and deleting courses changes `courses.json`. Replace ID `1` in the examples with the `id` returned when you create a course.

### Create a Course

```powershell
@'
{
	"name": "Python Basics",
	"description": "Learn Python fundamentals including variables, loops, and functions",
	"target_date": "2026-12-31",
	"status": "Not Started"
}
'@ | curl.exe -i -X POST http://localhost:5000/api/courses -H "Content-Type: application/json" --data-binary '@-'
```

Expected: `201 Created`, with the created course, its generated `id`, and a UTC `created_at` timestamp.

All four fields above are required. Dates use `YYYY-MM-DD`. Allowed statuses are `Not Started`, `In Progress`, and `Completed`.

### List All Courses

```powershell
curl.exe -i http://localhost:5000/api/courses
```

Expected: `200 OK`, with a JSON array of courses, or `[]` when there are none.

### Get a Course

```powershell
curl.exe -i http://localhost:5000/api/courses/1
```

Expected: `200 OK`, with the course if ID `1` exists; otherwise `404 Not Found`.

### Update a Course

Partial updates are supported; only include fields you want to change.

```powershell
@'
{"status": "In Progress"}
'@ | curl.exe -i -X PUT http://localhost:5000/api/courses/1 -H "Content-Type: application/json" --data-binary '@-'
```

Expected: `200 OK`, with the updated course if ID `1` exists; otherwise `404 Not Found`.

### Delete a Course

```powershell
curl.exe -i -X DELETE http://localhost:5000/api/courses/1
```

Expected: `200 OK` if ID `1` exists, with:

```json
{"message": "Course with id 1 deleted."}
```

If the course does not exist, expect `404 Not Found`.

## Error Examples

### Missing Required Fields

```powershell
@'
{"name": "Incomplete Course"}
'@ | curl.exe -i -X POST http://localhost:5000/api/courses -H "Content-Type: application/json" --data-binary '@-'
```

Expected: `400 Bad Request`, with:

```json
{"error": "Missing required field: 'description'"}
```

### Invalid Status

```powershell
@'
{
	"name": "Test Course",
	"description": "Test",
	"target_date": "2026-12-31",
	"status": "Invalid Status"
}
'@ | curl.exe -i -X POST http://localhost:5000/api/courses -H "Content-Type: application/json" --data-binary '@-'
```

Expected: `400 Bad Request`, with:

```json
{"error": "Invalid status value. Allowed values are: ['Not Started', 'In Progress', 'Completed']"}
```

### Request a Missing Course

```powershell
curl.exe -i http://localhost:5000/api/courses/999
```

Expected: `404 Not Found` if ID `999` does not exist, with:

```json
{"error": "Course not found"}
```

