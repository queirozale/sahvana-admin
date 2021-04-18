import os

from flask import Flask
from flask import request
from flask_cors import CORS

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello World!!"

@app.route('/hello', methods=['GET', 'POST'])
def api():
    content = request.get_json(force=True)
    return content

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)