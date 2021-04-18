import os
from flask import Flask, request
from flask_cors import CORS
from dotenv import dotenv_values
from pymongo import MongoClient
import json
from bson import ObjectId

app = Flask(__name__)
CORS(app, support_credentials=True)

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

def create_product(data):
    client = MongoClient(os.environ['DATABASE_URL'])
    db = client['sahvana-dev']
    collection = db['products']
    collection.insert_one(data)

def find_product():
    client = MongoClient(os.environ['DATABASE_URL'])
    db = client['sahvana-dev']
    collection = db['products']

    return list(collection.find({}))


@app.route('/')
def index():
    return f"<h1>Welcome to our server !!</h1>"

@app.route('/api/create_product', methods=['GET', 'POST'])
def api_create_product():
    content = request.get_json(force=True)
    try:
        create_product(content)
        result = "Product created"
    except:
        result = "Error"
    return result

@app.route('/api/find_product', methods=['GET'])
def api_find_product():
    try:
        result = JSONEncoder().encode(find_product())
    except:
        result = "Error"

    return result

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True)