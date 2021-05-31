from datetime import date, timedelta
import requests


class ShopifyOrder:
    def __init__(self, config):
        API_KEY = config["SHOPIFY_API_KEY"]
        PASSWORD = config["SHOPIFY_PASSWORD"]
        SHOP_NAME = config["SHOP_NAME"]

        self.shop_url = f"https://{API_KEY}:{PASSWORD}@{SHOP_NAME}.myshopify.com/admin"


    def get_total(self):
        base_orders_url = self.shop_url + "/api/2021-04/orders.json?status=any"
        total_orders = []

        frequency = 7 # days
        n_cycles = 60
        end_date = date.today()
        for _ in range(n_cycles):
            start_date = end_date - timedelta(days=frequency)

            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")

            query = f"&created_at_min={start_date}&created_at_max={end_date}&limit=250"
            orders_url = base_orders_url + query

            r = requests.get(orders_url)
            orders = r.json()['orders']
            total_orders += orders

            print(f"Period from: {start_date_str} to: {end_date_str} finished!")

            end_date = start_date
            
        return total_orders
