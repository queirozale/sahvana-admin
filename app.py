import os
from flask import Flask, request
from flask_cors import CORS
from dotenv import dotenv_values
from pymongo import MongoClient

app = Flask(__name__)
CORS(app, support_credentials=True)


def create_product(data):
    client = MongoClient(os.environ['DATABASE_URL'])
    db = client['sahvana-dev']
    collection = db['products']
    collection.insert_one(data)


@app.route('/')
def index():
    return f"<h1>Welcome to our server !!</h1>"

@app.route('/api/create_product', methods=['GET', 'POST'])
def api():
    content = request.get_json(force=True)
    try:
        create_product(content)
        result = "Product created"
    except:
        result = "Error"
    return result

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True)