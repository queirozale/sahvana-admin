from pymongo import MongoClient

class SahvanaSales:
    def __init__(self, config):
        mongo_url = config["DATABASE_URL"]
        client = MongoClient(mongo_url)
        db = client["sahvana-dev"]
        self.collection = db["sales"]


    def find_by_vendor(self, vendor):
        query = {'vendor': vendor}

        return list(self.collection.find(query))

    
    def add(self, sales):
        self.collection.insert_many(sales)
