from pymongo import MongoClient

class SahvanaSales:
    def __init__(self, config):
        mongo_url = config["DATABASE_URL"]
        client = MongoClient(mongo_url)
        db = client["sahvana-dev"]
        self.collection = db["sales"]


    def find_by_vendor(self, vendor):
        query = {'vendor': vendor}
        results = list(self.collection.find(query))
        results_ = []
        for r in results:
            r_ = {}
            for k in r.keys():
                if k == "_id":
                    r_[k] = str(r[k])
                else:
                    r_[k] = r[k]

            results_.append(r_)

        return results_

    
    def add(self, sales):
        self.collection.insert_many(sales)
