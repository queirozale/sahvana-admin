import requests
import shopify
from datetime import date

from .utils import get_payload


class ShopifyProduct:
    def __init__(self, config):
        API_KEY = config["SHOPIFY_API_KEY"]
        PASSWORD = config["SHOPIFY_PASSWORD"]
        SHOP_NAME = config["SHOP_NAME"]

        self.shop_url = f"https://{API_KEY}:{PASSWORD}@{SHOP_NAME}.myshopify.com/admin"
        self.products = []


    def create(self, data):
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        payload = get_payload(data)
        product_url = self.shop_url + "/api/2021-04/products.json"

        r = requests.post(product_url, json=payload,  headers=headers)

        if r.status_code == 201:
            print("Product successfully saved!")


    def edit_product_format(self, product):
        new_product_format = product.attributes

        new_formats = {
            'variants': [],
            'options': [],
            'images': [],
        }

        for property in new_formats.keys():
            for p in new_product_format[property]:
                new_formats[property].append(p.attributes)

            new_product_format.update({property: new_formats[property]})

        new_product_format['image'] = new_product_format['image'].attributes
    
        return new_product_format

    
    def read_all(self):
        shopify.ShopifyResource.set_site(self.shop_url)
        current_page = shopify.Product.find()
        products = current_page
        counter = 0
        print(f"Page {counter} completed!")
        while current_page.has_next_page():
            next_page = current_page.next_page()
            current_page = next_page
            products += current_page
            counter += 1
            print(f"Page {counter} completed!")
        
        for product in products:
            try:
                product_ = self.edit_product_format(product)
                self.products.append(product_)
            except:
                print("Error reading product")


    def read_news(self):
        today = date.today().strftime("%Y-%m-%d")
        product_url = self.shop_url + f"/api/2021-04/products.json?updated_at_min={today}"
        r = requests.get(product_url)

        current_ids = []
        for prod in self.products:
            current_ids.append(prod["id"])

        for prod in r.json()['products']:
            if prod["id"] not in current_ids:
                self.products.append(prod)


    def find_by_title(self, title):
        for prod in self.products:
            if prod['title'] == title:
                return prod
     

    def find_by_vendor(self, vendor):
        selected_products = []
        for prod in self.products:
            if prod['vendor'] == vendor:
                selected_products.append(prod)

        return selected_products


    def find_by_sku(self, sku):
        found = False
        for prod in self.products:
            for variant in prod['variants']:
                if variant['sku'] == sku:
                    result = prod
                    found = True

        if not found:
            result = {"error": "not found"}
            
        return result


    def update(self, data):
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        payload = get_payload(data)

        self.read_news()

        product = self.find_by_sku(sku=str(data["_id"]))

        if "error" not in list(product.keys()):
            product_id = product["id"]
            product_url = self.shop_url + f"/api/2021-04/products/{product_id}.json"
            r = requests.put(product_url, json=payload,  headers=headers)

            if r.status_code == 200:
                print("Product successfully updated!")
            else:
                print("Error on product update!")
        else:
            print("Product not found")


    def delete(self, _id):
        self.read_news()

        product = self.find_by_sku(sku=str(_id))

        if "error" not in list(product.keys()):
            product_id = product["id"]
            product_url = self.shop_url + f"/api/2021-04/products/{product_id}.json"
            r = requests.delete(product_url)

            if r.status_code == 200:
                print("Product successfully deleted!")
            else:
                print("Error on product delete!")
        else:
            print("Product not found")


