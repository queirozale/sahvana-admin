import os
from flask import Flask, request, render_template, abort
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv
from pymongo import MongoClient
import json
from bson import ObjectId
import pandas as pd
import shopify
from shopify.resources import product
import hmac
import hashlib
import base64

from sahvana_tools.product import SahvanaProduct
from integration.product import ShopifyProduct

app = Flask(__name__)
CORS(app, support_credentials=True)

config = {
    "DATABASE_URL": os.environ["DATABASE_URL"],
    "SHOPIFY_API_KEY": os.environ["SHOPIFY_API_KEY"],
    "SHOPIFY_PASSWORD": os.environ["SHOPIFY_PASSWORD"],
    "SHOP_NAME": os.environ["SHOP_NAME"],
    "IMGBB_API_KEY": os.environ["IMGBB_API_KEY"],
}

sahvana_product = SahvanaProduct(config)
shopify_product = ShopifyProduct(config)

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/create_product', methods=['GET', 'POST'])
def api_create_product():
    content = request.get_json(force=True)
    sahvana_product.create(data=content)
    shopify_product.create(data=content)

    result = "Product created"

    return result


@app.route('/api/update_product', methods=['GET', 'POST'])
def api_update_product():
    content = request.get_json(force=True)
    sahvana_product.update(data=content)
    shopify_product.update(data=content)

    result = "Product updated"

    return result


@app.route('/api/delete_product', methods=['GET', 'POST'])
def api_delete_product():
    content = request.get_json(force=True)
    sahvana_product.delete(_id=content["_id"])
    shopify_product.delete(_id=content["_id"])

    result = "Product deleted"

    return result

@app.route('/api/find_product', methods=['GET', 'POST'])
@cross_origin()
def api_find_product():
    content = request.get_json(force=True)
    try:
        result = JSONEncoder().encode(sahvana_product.find_all(content['email']))
    except:
        result = "Error"

    return result

@app.route('/webhook', methods=['GET', 'POST'])
def handle_webhook():
    data = request.get_json(force=True)
    # verified = verify_webhook(data, request.headers.get('X-Shopify-Hmac-SHA256'))
    print(config)

    return config


# @app.route('/api/agg_orders', methods=['GET', 'POST'])
# def api_agg_orders():
#     content = request.get_json(force=True)
#     result = get_agg_orders(content['Vendor'])

#     return result


# @app.route('/api/total_sales', methods=['GET', 'POST'])
# def api_total_sales():
#     content = request.get_json(force=True)
#     result = get_sum_sales(content['Vendor'])

#     return result  


# @app.route('/api/orders', methods=['GET', 'POST'])
# def api_orders():
#     content = request.get_json(force=True)
#     result = get_orders(content['Vendor'])

#     return result  


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True)


# .\env\Scripts\activate
# set FLASK_APP=app
# set FLASK_ENV=development
# flask run