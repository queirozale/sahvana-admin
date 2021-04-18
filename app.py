import os
from flask import Flask, request
from flask_cors import CORS
from dotenv import dotenv_values

app = Flask(__name__)
CORS(app, support_credentials=True)

config = dotenv_values(".env")

def create_product(data):
    mongo_url = "mongodb+srv://queirozale7:v1-vs4%3Dx@cluster0.x6emw.mongodb.net/test"
    client = MongoClient(mongo_url)
    db = client["jeco"]
    collection = db["crawler-results"]

@app.route('/')
def index():
    return f"<h1>Welcome to our server {config['TEST_API']} !!</h1>"

@app.route('/api/create_product', methods=['GET', 'POST'])
def api():
    content = request.get_json(force=True)
    return content

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True)