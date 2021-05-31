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
