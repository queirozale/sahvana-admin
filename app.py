import os
from flask import Flask, request, render_template
from flask_cors import CORS
from dotenv import dotenv_values
from pymongo import MongoClient
import json
from bson import ObjectId
import shopify
import requests

app = Flask(__name__)
CORS(app, support_credentials=True)

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

def save_image_imgbb(img):
    img = img.split('base64,')[1]
    img = img.encode("utf-8")

    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": os.environ['IMGBB_API_KEY'],
        "image": img,
    }
    res = requests.post(url, payload)
    img_url = res.json()['data']['url']

    return img_url 

def create_product(data):
    client = MongoClient(os.environ['DATABASE_URL'])
    db = client['sahvana-dev']
    collection = db['products']
    collection.insert_one(data)

def find_product(email):
    client = MongoClient(os.environ['DATABASE_URL'])
    db = client['sahvana-dev']
    collection = db['products']
    query = {'email': email}

    return list(collection.find(query))

def save_products():
    shop_url = "https://{}:{}@{}.myshopify.com/admin".format(
        os.environ['SHOPIFY_API_KEY'], 
        os.environ['SHOPIFY_PASSWORD'], 
        os.environ['SHOP_NAME']
    )
    shopify.ShopifyResource.set_site(shop_url)

    db_products = find_product()
    for db_prodcut in db_products:
        product = shopify.Product()
        print(db_prodcut['title'])
        product.title = db_prodcut['title']
        product.id
        product.status = "draft"
        product.save()

    # image = shopify.Image()
    # image.src = img_url
    # product.images = [image] # Here's the change

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/create_product', methods=['GET', 'POST'])
def api_create_product():
    content = request.get_json(force=True)
    # try:
    images = content['imageFiles']
    images_url = []
    for img in images:
        if img != None:
            img_url = save_image_imgbb(img[0])
            images_url.append(img_url)

    content['imageFiles'] = images_url
    create_product(content)
    result = "Product created"
    # except:
    #     result = "Error"
    return result

@app.route('/api/find_product', methods=['GET', 'POST'])
def api_find_product():
    content = request.get_json(force=True)
    try:
        result = JSONEncoder().encode(find_product(content['email']))
    except:
        result = "Error"

    return result

@app.route('/api/save_products', methods=['GET', 'POST'])
def api_save_products():
    try:
        save_products()
        result = "Product saved"
    except:
        result = "Error"

    return result


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True)


# .\env\Scripts\activate
# set FLASK_APP=app
# set FLASK_ENV=development
# flask run