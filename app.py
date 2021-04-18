import os

from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, support_credentials=True)

@app.route('/')
def index():
    return "<h1>Welcome to our server !!</h1>"

@app.route('/api', methods=['GET', 'POST'])
def api():
    content = request.get_json(force=True)
    return content

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)