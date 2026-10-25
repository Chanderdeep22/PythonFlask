# Flask & MongoDB — DevOps Assignment

**Student:** Chanderdeep Singh Sandhu  
**GitHub repository:** https://github.com/Chanderdeep22/PythonFlask

This Flask application demonstrates the two assignment tasks:
- `GET /api` reads a JSON list from `backend_data.json` and returns it as JSON.
- The frontend form sends a name, email address and optional message for insertion into MongoDB Atlas.
- On a successful insert, the server redirects to `/success`, displaying **Data submitted successfully**.
- On validation or database/configuration error, the error is shown on the original form page without redirecting.

## Files
- `app.py` — Flask API, form validation, MongoDB insertion and routes.
- `backend_data.json` — file-backed JSON list for `/api`.
- `templates/index.html`, `templates/success.html` — form and success page.
- `static/styles.css`, `static/app.js` — original user styling plus updated success/error navigation behavior.
- `requirements.txt` — dependencies.
- `.env.example` — placeholder configuration; no real credentials are included.
- `.gitignore` — excludes `.env`, virtual environments and Python cache files.
- `tests/test_app.py` — test-client tests with MongoDB writes mocked.
- `preflight_check.py` — dependency-free source/configuration checks.
- `Documentation.docx` — explanations, commands, screenshots and caveats.
- `screenshots/` — actual output captures from local file/preflight checks.
- `test_results.txt` — verification scope and commands.

## Setup (Windows PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```
Edit `.env` and set `MONGO_URI` to your own MongoDB Atlas connection string. Configure a database user and allow your machine's IP address in Atlas Network Access. Do not commit `.env`.

## Run
```powershell
python app.py
```
Open `http://127.0.0.1:5000/` for the form and `http://127.0.0.1:5000/api` for the JSON list.

## Test
```powershell
python preflight_check.py
python -m unittest discover -s tests -v
```
The package-preparation environment could not install Flask/PyMongo because package repository access was unavailable. The dependency-free preflight check passes 13/13 checks, but the Flask test-client tests and live Atlas write have not been executed here. After setup, run the tests and manually verify both success and failure paths against your Atlas cluster.

## Security
The form intentionally does not collect passwords. No real `.env` file or database credentials are included. If a real Atlas credential was uploaded in a previous copy, rotate it before publishing.


## Publication status
The repository URL above was supplied by the student. This ZIP includes that URL, but the remote repository was not verified as updated with this final ZIP. Make sure the files are pushed to GitHub before submission.
