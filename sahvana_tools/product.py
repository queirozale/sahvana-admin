from pymongo import MongoClient
from bson import ObjectId
import requests


class SahvanaProduct:
    def __init__(self, config):
        self.DATABASE_URL = config["DATABASE_URL"]
        self.IMGBB_API_KEY = config["IMGBB_API_KEY"]
        self.client = MongoClient(self.DATABASE_URL)
        self.db = self.client['sahvana-dev']
        self.collection = self.db['products']


    def save_image_imgbb(self, img):
        img = img.split('base64,')[1]
        img = img.encode("utf-8")

        url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": self.IMGBB_API_KEY,
            "image": img,
        }
        res = requests.post(url, payload)
        img_url = res.json()['data']['url']

        return img_url


    def create(self, data):
        images = data['imageFiles']
        images_url = []
        for img in images:
            if img != None:
                img_url = self.save_image_imgbb(img[0])
                images_url.append(img_url)

        data['imageFiles'] = images_url

        self.collection.insert_one(data)


    def update(self, data):
        images = data['imageFiles']
        images_url = []
        for img in images:
            if img != None:
                if type(img) == list:
                    img_url = self.save_image_imgbb(img[0])
                else:
                    img_url = img
                images_url.append(img_url)

        data['imageFiles'] = images_url

        query = {"_id": ObjectId(data['_id'])}
        data['_id'] = ObjectId(data['_id'])
        new_values = {"$set": data}

        self.collection.update_one(query, new_values)


    def delete(self, _id):
        query = {"_id": ObjectId(_id)}
        self.collection.delete_one(query)


    def find(self, _id):
        query = {"_id": ObjectId(_id)}

        return list(self.collection.find(query))[0]
    
    def find_all(self, email):
        # special permission
        if email in ['queirozalessandro1@gmail.com', 'sahvana.dev@gmail.com']:
            return list(self.collection.find())
        else:
            query = {'email': email}
            return list(self.collection.find(query))
