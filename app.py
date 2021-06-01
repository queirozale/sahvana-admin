import os
from flask import Flask, request, render_template
from flask_cors import CORS
import json
from bson import ObjectId
from datetime import datetime, date, timedelta

from sahvana_tools.product import SahvanaProduct
from sahvana_tools.order import SahvanaOrder
from sahvana_tools.sales import SahvanaSales
from sahvana_tools.utils import get_sales_by_date_range, get_agg_sales, get_sales
from integration.shopify.utils import data_migration, store_migration_errors
from integration.shopify.product import ShopifyProduct
from integration.auth0.users import Auth0User

app = Flask(__name__)
CORS(app, support_credentials=True)

config = {
    "DATABASE_URL": os.environ["DATABASE_URL"],
    "SHOPIFY_API_KEY": os.environ["SHOPIFY_API_KEY"],
    "SHOPIFY_PASSWORD": os.environ["SHOPIFY_PASSWORD"],
    "SHOP_NAME": os.environ["SHOP_NAME"],
    "IMGBB_API_KEY": os.environ["IMGBB_API_KEY"],
    "AUTH0_CLIENT_ID": os.environ["AUTH0_CLIENT_ID"],
    "AUTH0_CLIENT_SECRET": os.environ["AUTH0_CLIENT_SECRET"],
    "AUTH0_DOMAIN": os.environ["AUTH0_DOMAIN"]
}

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

    sahvana_product = SahvanaProduct(config)
    shopify_product = ShopifyProduct(config)

    sahvana_product.create(data=content)
    shopify_product.create(data=content)

    result = "Product created"

    return result


@app.route('/api/update_product', methods=['GET', 'POST'])
def api_update_product():
    content = request.get_json(force=True)
    
    sahvana_product = SahvanaProduct(config)
    shopify_product = ShopifyProduct(config)

    sahvana_product.update(data=content)
    shopify_product.update(data=content)


    result = "Product updated"

    return result


@app.route('/api/delete_product', methods=['GET', 'POST'])
def api_delete_product():
    content = request.get_json(force=True)

    sahvana_product = SahvanaProduct(config)
    shopify_product = ShopifyProduct(config)

    sahvana_product.delete(_id=content["_id"])
    shopify_product.delete(_id=content["_id"])

    result = "Product deleted"

    return result


@app.route('/api/find_product', methods=['GET', 'POST'])
def api_find_product():
    content = request.get_json(force=True)

    sahvana_product = SahvanaProduct(config)

    try:
        result = JSONEncoder().encode(sahvana_product.find_all(content['email']))
    except:
        result = "Error"

    return result


@app.route('/api/last_orders', methods=['GET', 'POST'])
def api_get_last_orders():
    sahvana_order = SahvanaOrder(config)

    result = JSONEncoder().encode(sahvana_order.get_last())

    return result


@app.route('/api/sales', methods=['GET', 'POST'])
def api_get_sales():
    content = request.get_json(force=True)
    email = content["email"]
    
    auth0_user = Auth0User(config)
    users_list = auth0_user.find_all()

    for user in users_list:
        if user["email"] == email:
            vendor = user["nickname"]

    try:
        sahvana_sales = SahvanaSales(config)
        sales = sahvana_sales.find_by_vendor(vendor)
        max_date = date.today()
        min_date = max_date - timedelta(days=365)
        max_date = datetime.strftime(max_date, "%Y-%m-%d")
        min_date = datetime.strftime(min_date, "%Y-%m-%d")
        filtered_sales = get_sales_by_date_range(sales, min_date, max_date)
        data = get_agg_sales(filtered_sales)
        data.update({'chart_data': [v for v in data['chart_data'].values()]})
        data["last_sales"] = filtered_sales[-5:]
    except:
        data = {
            "chart_data": [
                {
                    "date": None,
                    "price": None
                }
            ],
            "last_sales": [],
            "sum_sales": 0
        }

    return data


@app.route('/api/create_user', methods=['GET', 'POST'])
def api_create_user():
    content = request.get_json(force=True)
    vendor = content["nickname"]
    user_keys = ["email", "name", "nickname", "password"]
    additional_data = {
        "blocked": False,
        "email_verified": False,
        "connection": "Username-Password-Authentication",
    }
    data = dict({k: content[k] for k in user_keys}, **additional_data)
    auth0_user = Auth0User(config)
    result = auth0_user.create(data)
    users_list = auth0_user.find_all()

    if content["data_migration"]:
        try:
            shopify_product = ShopifyProduct(config)
            sahvana_product = SahvanaProduct(config)
            shopify_product.read_all()
            products = shopify_product.find_by_vendor(vendor=vendor)
            print(f"{len(products)} products found")
            error_products = []
            for product in products:
                migrated_data = data_migration(users_list=users_list, prod=product)
                print(migrated_data['title'])
                try:
                    sahvana_product.create(data=migrated_data)
                except:
                    error_products.append(migrated_data['title'])

            if len(error_products) > 0:
                store_migration_errors(config, vendor, error_products)

            result["data_migration"] = "Success"
        except:
            result["data_migration"] = "Error"

    print(result)

    return result

@app.route('/webhook', methods=['GET', 'POST'])
def handle_webhook():
    content = request.get_json(force=True)

    sahvana_order = SahvanaOrder(config)
    sahvana_order.add(content)

    sahvana_sales = SahvanaSales(config)
    sales = get_sales(content)
    sahvana_sales.add(sales)

    result = "Order successfully added!"
    print(result)

    return result

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True)


# .\env\Scripts\activate
# set FLASK_APP=app
# set FLASK_ENV=development
# flask run