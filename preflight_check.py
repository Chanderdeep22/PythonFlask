"""Dependency-free source/configuration checks for the submission package."""
import ast
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
checks = []

def check(label, condition, detail=""):
    checks.append((label, bool(condition), detail))

required = [
    "app.py", "backend_data.json", "requirements.txt", ".env.example", ".gitignore",
    "README.md", "templates/index.html", "templates/success.html",
    "static/styles.css", "static/app.js", "tests/test_app.py"
]
check("Required project files exist", all((ROOT / f).is_file() for f in required))
for rel in ["app.py", "tests/test_app.py"]:
    try:
        ast.parse((ROOT / rel).read_text(encoding="utf-8"), filename=rel)
        ok = True
    except (SyntaxError, OSError):
        ok = False
    check(f"Python syntax: {rel}", ok)
try:
    records = json.loads((ROOT / "backend_data.json").read_text(encoding="utf-8"))
    check("backend_data.json parses as a list", isinstance(records, list))
except (OSError, json.JSONDecodeError):
    check("backend_data.json parses as a list", False)
    records = []
app_source = (ROOT / "app.py").read_text(encoding="utf-8")
index_html = (ROOT / "templates/index.html").read_text(encoding="utf-8")
success_html = (ROOT / "templates/success.html").read_text(encoding="utf-8")
check("GET /api route reads backend_data.json", '@app.get("/api")' in app_source and "DATA_FILE.open" in app_source)
check("POST /submit inserts through save_submission", '@app.post("/submit")' in app_source and "save_submission(submission)" in app_source)
check("Success route uses required message", '@app.get("/success")' in app_source and "Data submitted successfully" in success_html)
js_source = (ROOT / "static/app.js").read_text(encoding="utf-8")
check("Frontend redirects after successful insert", "window.location.assign(result.redirect_url)" in js_source and "id=\"form-feedback\"" in index_html)
check("Form uses non-sensitive fields", 'name="name"' in index_html and 'name="email"' in index_html and 'name="message"' in index_html and 'name="password"' not in index_html)
check("Mongo URI reads from environment", 'os.getenv("MONGO_URI"' in app_source and "MONGO_URI=" in (ROOT / ".env.example").read_text(encoding="utf-8"))
check("Secrets and bytecode are ignored", ".env" in (ROOT / ".gitignore").read_text(encoding="utf-8") and not (ROOT / ".env").exists())
req = (ROOT / "requirements.txt").read_text(encoding="utf-8")
check("Dependencies listed", "Flask" in req and "pymongo[srv]" in req and "python-dotenv" in req)
check("GitHub repository URL is included", "https://github.com/Chanderdeep22/PythonFlask" in (ROOT / "README.md").read_text(encoding="utf-8"))

passed = sum(ok for _, ok, _ in checks)
for label, ok, _ in checks:
    print(f"{'PASS' if ok else 'FAIL'}  {label}")
print(f"\nSummary: {passed}/{len(checks)} preflight checks passed.")
print("Note: these checks do not connect to MongoDB Atlas or replace the Flask unit tests.")
sys.exit(0 if passed == len(checks) else 1)
