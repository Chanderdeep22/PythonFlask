import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pymongo.errors import PyMongoError
import app as flask_app


class FlaskMongoAssignmentTests(unittest.TestCase):
    def setUp(self):
        flask_app.app.config.update(TESTING=True, MONGO_URI="")
        self.client = flask_app.app.test_client()

    def test_api_returns_list_from_backend_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_file = Path(tmp) / "backend_data.json"
            data_file.write_text(json.dumps([{"id": 9, "name": "Test"}]), encoding="utf-8")
            with patch.object(flask_app, "DATA_FILE", data_file):
                response = self.client.get("/api")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [{"id": 9, "name": "Test"}])

    def test_api_rejects_invalid_json_file_safely(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_file = Path(tmp) / "backend_data.json"
            data_file.write_text("{invalid", encoding="utf-8")
            with patch.object(flask_app, "DATA_FILE", data_file):
                response = self.client.get("/api")
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.get_json())

    def test_successful_insert_redirects_to_success_page(self):
        form = {"name": "Alex Example", "email": "alex@example.com", "message": "Hello"}
        with patch.object(flask_app, "save_submission") as save:
            response = self.client.post("/submit", data=form)
        self.assertEqual(response.status_code, 303)
        self.assertTrue(response.headers["Location"].endswith("/success"))
        self.assertEqual(save.call_args.args[0]["name"], "Alex Example")
        self.assertNotIn("password", save.call_args.args[0])


    def test_ajax_success_returns_redirect_json(self):
        form = {"name": "Alex Example", "email": "alex@example.com", "message": "Hello"}
        with patch.object(flask_app, "save_submission") as save:
            response = self.client.post("/submit", data=form, headers={"Accept": "application/json"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["redirect_url"].endswith("/success"))
        self.assertEqual(save.call_args.args[0]["name"], "Alex Example")

    def test_ajax_validation_error_returns_json_without_redirect(self):
        response = self.client.post(
            "/submit", data={"name": "", "email": ""}, headers={"Accept": "application/json"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_missing_required_fields_stays_on_form(self):
        response = self.client.post("/submit", data={"name": "", "email": ""})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Please enter both your name and email address.", response.data)

    def test_bad_email_stays_on_form(self):
        response = self.client.post("/submit", data={"name": "Alex", "email": "not-an-email"})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Please enter a valid email address.", response.data)

    def test_unconfigured_atlas_stays_on_form(self):
        with patch.object(flask_app, "save_submission", side_effect=flask_app.MongoConfigurationError()):
            response = self.client.post(
                "/submit", data={"name": "Alex", "email": "alex@example.com", "message": ""}
            )
        self.assertEqual(response.status_code, 503)
        self.assertIn(b"MongoDB Atlas is not configured.", response.data)

    def test_database_error_stays_on_form(self):
        with patch.object(flask_app, "save_submission", side_effect=PyMongoError("synthetic test error")):
            response = self.client.post(
                "/submit", data={"name": "Alex", "email": "alex@example.com", "message": ""}
            )
        self.assertEqual(response.status_code, 503)
        self.assertIn(b"The data could not be saved.", response.data)

    def test_success_page_contains_required_message(self):
        response = self.client.get("/success")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Data submitted successfully", response.data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
