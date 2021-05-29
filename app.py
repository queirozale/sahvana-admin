import os
from flask import Flask, request, render_template
from flask_cors import CORS
from dotenv import dotenv_values
from pymongo import MongoClient
import json
from bson import ObjectId
import shopify
import requests
import pandas as pd

from sahvana_tools.product import SahvanaProduct
from integration.product import ShopifyProduct

app = Flask(__name__)
CORS(app, support_credentials=True)

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

config = {
    "DATABASE_URL": os.environ["DATABASE_URL"],
    "SHOPIFY_API_KEY": os.environ["SHOPIFY_API_KEY"],
    "SHOPIFY_PASSWORD": os.environ["SHOPIFY_PASSWORD"],
    "SHOP_NAME": os.environ["SHOP_NAME"],
    "IMGBB_API_KEY": os.environ["IMGBB_API_KEY"],
}

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
    if email == 'queirozalessandro1@gmail.com':
        return list(collection.find())
    else:
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
        # image = shopify.Image()
        # image.src = img_url
        # product.images = [image]
        product.save()

def get_agg_orders(vendor):
    client = MongoClient(os.environ['DATABASE_URL'])
    db = client["sahvana-dev"]
    collection = db["orders"]

    query = {'Vendor': vendor}
    results = list(collection.find(query))

    sales, dates = [], []
    for result in results :
        dates.append(result['Paid at'])
        sales.append(result['Subtotal'])

    df = pd.DataFrame({
        'Paid at': dates,
        'Subtotal': sales
    })
    df.sort_values(by='Paid at', inplace=True)
    df.set_index('Paid at', inplace=True)

    g = df.groupby(pd.Grouper(freq="M"))
    df = g.sum().reset_index()

    data = []
    for i in range(len(df)):
        date = df.iloc[i]['Paid at']
        date = date.strftime("%d-%m-%Y")
        sales = df.iloc[i]['Subtotal']
        data.append({'time': date, 'amount': sales})
        
    return {'data': data}

def get_sum_sales(vendor):
    client = MongoClient(os.environ['DATABASE_URL'])
    db = client["sahvana-dev"]
    collection = db["orders"]

    query = {'Vendor': vendor}
    results = list(collection.find(query))

    total_sales = 0
    for result in results:
        total_sales += result['Subtotal']

    return {'total_sales': total_sales}

def get_orders(vendor):
    client = MongoClient(os.environ['DATABASE_URL'])
    db = client["sahvana-dev"]
    collection = db["orders"]

    query = {'Vendor': vendor}
    results = list(collection.find(query))
    last_results = results[-5:]
    last_results = last_results[::-1]

    data = []
    c = 0
    for result in last_results:
        date = result['Paid at']
        date = date.strftime("%d-%m-%Y")
        name = result['Billing Name']
        shipTo = result['Shipping City'] + ',' + result['Shipping Province']
        product = result['Lineitem name']
        amount = result['Subtotal']
        data.append({
            'id': c,
            'date': date,
            'name': name,
            'shipTo': shipTo,
            'product': product,
            'amount': amount
        })
        c += 1

    return {'data': data}

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

@app.route('/api/agg_orders', methods=['GET', 'POST'])
def api_agg_orders():
    content = request.get_json(force=True)
    result = get_agg_orders(content['Vendor'])

    return result

@app.route('/api/total_sales', methods=['GET', 'POST'])
def api_total_sales():
    content = request.get_json(force=True)
    result = get_sum_sales(content['Vendor'])

    return result  

@app.route('/api/orders', methods=['GET', 'POST'])
def api_orders():
    content = request.get_json(force=True)
    result = get_orders(content['Vendor'])

    return result  

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True)


# .\env\Scripts\activate
# set FLASK_APP=app
# set FLASK_ENV=development
# flask run