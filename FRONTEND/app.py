from datetime import datetime
import requests
from flask import Flask, current_app, jsonify, render_template, request

app = Flask(__name__)

backend_url = "http://127.0.0.1:9000"


@app.route('/')
def home():
    current_time = datetime.now().strftime("%H:%M:%S")
    current_Date = datetime.today().strftime("%Y-%m-%d")
    current_day = datetime.today().strftime("%A")

    return render_template(
        'index.html',
        current_time=current_time,
        current_Date=current_Date,
        current_day=current_day,
        backend_url=backend_url,
    )

@app.route('/submit', methods=['POST'])
def submit():
    form_data = dict(request.form)
    try:
        response = requests.post(
            f"{backend_url}/submit",
            json=form_data,
            timeout=10,
        )
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as error:
        current_app.logger.error("Backend submission failed: %s", error)
        return jsonify(error="Unable to save submission. Check the backend server."), 502


@app.route('/get_data')
def get_data():
    try:
        response = requests.get(f"{backend_url}/view", timeout=10)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as error:
        current_app.logger.error("Backend data request failed: %s", error)
        return jsonify(error="Unable to fetch data. Check the backend server."), 502

if __name__ == "__main__":
    app.run(debug=True)