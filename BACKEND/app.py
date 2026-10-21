from flask import Flask, jsonify, request
import pymongo
from dotenv import load_dotenv
import os
import requests
#from urllib.parse import urlsplit

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = pymongo.MongoClient(MONGO_URI)

db =client.test

collection = db["FLASK_TUTORIAL"]

app = Flask(__name__)


#@app.after_request
#def allow_frontend_origin(response):
#    origin = request.headers.get("Origin")
#    if origin:
#        parsed_origin = urlsplit(origin)
#        if parsed_origin.scheme == "http" and parsed_origin.hostname in {
#            "localhost",
#            "127.0.0.1",
#            "::1",
#        }:
#            response.headers["Access-Control-Allow-Origin"] = origin
#            response.headers.add("Vary", "Origin")
#    return response


@app.route("/submit", methods=["POST"])
def submit():
    form_data = request.get_json(silent=True)
    if not isinstance(form_data, dict):
        return jsonify(error="Expected a JSON object."), 400

    collection.insert_one(form_data)
    return jsonify(message="Data inserted successfully.")

@app.route("/view")
def view():
    data = list(collection.find())

    for item in data:
        print(item)

        del item["_id"]  # Remove the ObjectId field from the document

    data = {
        'data': data
    }
    return data
    #data = [
    #    {**document, "_id": str(document["_id"])}
    #    for document in collection.find()
    #]
    #return jsonify(data)

if __name__ == "__main__":

    app.run(port=9000,debug=True)