from .classifications import categoriesOptions, subcategoriesOptionsMale, subcategoriesOptionsFemale, subcategoriesOptionsGenderless
from pymongo import MongoClient

def get_payload(prod):
    has_variant = prod['has_variant']
    
    payload = {
        "product": {
            "title": prod["title"],
            "body_html": prod["description"],
            "vendor": prod["vendor"],
            "images": [
                {"src": img} for img in prod['imageFiles']
            ],
            "tags": [
                prod['gender'], 
                prod['category'], 
                prod['subcategory'], 
                prod['vendor']
            ],
        }
    }
    
    if has_variant:
        variants = []
        for k, v in prod['variantInventories'].items():
            variant = {}
            variant['sku'] = str(prod["_id"])
            if v == 0:
                v = prod['total_inventory']

            variant["inventory_policy"] = "deny"
            variant["fulfillment_service"] = "manual"
            variant["inventory_management"] = "shopify"
            variant["inventory_quantity"] = v
            if len(prod["promotional_price"]) > 0:
                variant["price"] = prod["promotional_price"]
                variant["compare_at_price"] = prod["variantPrices"][k]
            else:
                variant["price"] = prod["variantPrices"][k]
            variant["weight"] = prod["weight"]

            options = k.split('/')

            c = 1
            for opt in options:
                variant["option" + str(c)] = opt
                c += 1

            variant['taxable'] = False

            variants.append(variant)

        payload["product"]["variants"] = variants
        payload["product"]["options"] = [
            {"name": prod['variantType' + str(i)],
             "values": prod['inputOption' + str(i)]}
            for i in range(1, c)
        ]
    else:
        variant = {}
        variant['sku'] = str(prod["_id"])
        variant["inventory_policy"] = "deny"
        variant["fulfillment_service"] = "manual"
        variant["inventory_management"] = "shopify"
        variant["inventory_quantity"] = int(prod['total_inventory'])
        if len(prod["promotional_price"]) > 0:
            variant["price"] = prod["promotional_price"]
            variant["compare_at_price"] = prod["original_price"]
        else:
            variant["price"] = prod['original_price']
        variant["weight"] = prod["weight"]
        
        payload["product"]["variants"] = [variant]
    
    return payload


class ProductData:
    def __init__(self, prod):
        self.prod = prod
        self.data = {}
        
    def get_initial_attributes(self):
        attributes_dict = {
        'title': 'title',
        'body_html': 'description',
        'vendor': 'vendor',
        'tags': 'tags',
        'created_at': 'created_at',
        'updated_at': 'updated_at',
        }

        for (att, att_value) in attributes_dict.items():
            if att in ['created_at', 'updated_at']:
                self.data[att_value] = self.prod[att][:10]
            else:
                self.data[att_value] = self.prod[att]
        

    def check_has_variant(self):
        n_variants = len(self.prod['variants'])
        if n_variants == 1:
            self.data['has_variant'] = False
        else:
            self.data['has_variant'] = True
          
          
    def get_classifications(self):
        tags = self.prod['tags']
        genders = ['Masculino', 'Feminino', 'Unissex']
        gender = None
        category = None
        subcategory = None

        tags_list = []
        for tag in tags.split(','):
            tags_list.append(tag.strip())

        for tag in tags_list:
            for g in genders:
                if tag.lower() == g.lower():
                    gender = g

        if gender:
            categories = categoriesOptions[gender]
            for tag in tags_list:
                for c in categories:
                    if tag.lower() == c.lower():
                        category = c

            subs = {
                'Masculino': subcategoriesOptionsMale,
                'Feminino': subcategoriesOptionsFemale,
                'Unissex': subcategoriesOptionsGenderless
            }

            if category:
                subcategories = subs[gender]
                for tag in tags_list:
                    for s in subcategories[category]:
                        if tag.lower() == s.lower():
                            subcategory = s
                
        self.data['gender'] = gender
        self.data['category'] = category
        self.data['subcategory'] = subcategory
        
    
    @staticmethod
    def get_variant_values(variant_attributes):
        weight = variant_attributes['weight']
        inventory = variant_attributes['inventory_quantity']
        if variant_attributes['compare_at_price']:
            promotional_price = variant_attributes['price']
            original_price = variant_attributes['compare_at_price']
        else:
            promotional_price = None
            original_price = variant_attributes['price']

        return {
            'weight': weight,
            'total_inventory': inventory,
            'promotional_price': promotional_price,
            'original_price': original_price
        }


    def get_variant_attributes(self):
        variantPrices = {}
        variantInventories = {}

        if self.data['has_variant']:
            variants = self.prod['variants']
            for variant in variants:
                variant_attributes = variant
                variant_values = self.get_variant_values(variant_attributes)
                weight = variant_values['weight']
                promotional_price = variant_values['promotional_price']
                variantInventories[variant_attributes['title']] = variant_values['total_inventory']
                if promotional_price:
                    variantPrices[variant_attributes['title']] = promotional_price
                else:
                    variantPrices[variant_attributes['title']] = variant_values['original_price']
                
            total_inventory = sum(variantInventories.values())
            original_price = variant_values['original_price']
        else:
            default_attributes = self.prod['variants'][0]
            variant_values = self.get_variant_values(default_attributes)
            weight = variant_values['weight']
            promotional_price = variant_values['promotional_price']
            total_inventory = variant_values['total_inventory']
            original_price = variant_values['original_price']

        self.data['weight'] = weight
        self.data['total_inventory'] = total_inventory
        self.data['original_price'] = original_price
        self.data['promotional_price'] = promotional_price
        self.data['variantPrices'] = variantPrices
        self.data['variantInventories'] = variantInventories


    @staticmethod
    def get_variant_input_values(option_values, index_):
        try:
            variantType = list(option_values[index_].keys())[0]
            inputOption = list(option_values[index_].values())[0]
        except:
            variantType = None
            inputOption = []

        return variantType, inputOption


    def get_variant_option_values(self):
        options = self.prod['options']
        option_values = {}
        if options[0]['name'] != 'Title':
            c = 0
            for option in options:
                option_attributes = option
                option_values[c] = {option_attributes['name']: option_attributes['values']}
                c += 1

        for i in range(len(option_values.keys()), 3):
            option_values[i] = None

        variantType1, inputOption1 = self.get_variant_input_values(option_values, 0)
        variantType2, inputOption2 = self.get_variant_input_values(option_values, 1)
        variantType3, inputOption3 = self.get_variant_input_values(option_values, 2)

        self.data['variantType1'] = variantType1
        self.data['inputOption1'] = inputOption1
        self.data['variantType2'] = variantType2
        self.data['inputOption2'] = inputOption2
        self.data['variantType3'] = variantType3
        self.data['inputOption3'] = inputOption3
        
    def get_images(self):
        images = self.prod['images']
        imageFiles = []
        for image in images:
            imageFiles.append(image['src'])
            
        self.data['imageFiles'] = imageFiles
        
        
    def get_data(self):
        self.get_initial_attributes()
        self.get_classifications()
        self.check_has_variant()
        self.get_variant_attributes()
        self.get_variant_option_values()
        self.get_images()


def data_migration(users_list, prod):
    product_data = ProductData(prod)
    product_data.get_data()
    data = product_data.data
    vendor = prod['vendor']

    email = None
    for user in users_list:
        if user["nickname"] == vendor:
            email = user["email"]

    data['email'] = email

    return data


def store_migration_errors(config, vendor, error_products):
    DATABASE_URL = config["DATABASE_URL"]
    client = MongoClient(DATABASE_URL)
    db = client['sahvana-dev']
    collection = db['migration_errors']

    collection.insert_one({
        "vendor": vendor,
        "error_products": error_products
    })


