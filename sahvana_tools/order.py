from datetime import date, timedelta
import requests
from pymongo import MongoClient, DESCENDING


class SahvanaOrder:
    def __init__(self, config):
        mongo_url = config["DATABASE_URL"]
        client = MongoClient(mongo_url)
        db = client["sahvana-dev"]
        self.collection = db["orders"]


    def get_last(self):
        results = list(self.collection.find().sort('updated_at', DESCENDING))

        return results[:10]

    
    def get_vendor_orders(self, email):
        query = {'email': email}
        results = list(self.collection.find(query))


    def add(self, order):
        self.collection.insert_one(order)
