import requests
import os
from datetime import datetime
import pandas as pd

IMGBB_API_KEY = os.environ['IMGBB_API_KEY']

def save_image_imgbb(img):
    img = img.split('base64,')[1]
    img = img.encode("utf-8")

    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": IMGBB_API_KEY,
        "image": img,
    }
    res = requests.post(url, payload)
    img_url = res.json()['data']['url']

    return img_url


def get_images_url(images):
    images_url = []
    for img in images:
        if img != None:
            img_url = save_image_imgbb(img[0])
            images_url.append(img_url)

    return images_url


def get_sales(order):
    sales = []
    
    selected_attributes = [
        'name',
        'created_at',
        'updated_at',
        'financial_status',
        'contact_email',
    ]
    
    sales_info = [
        'vendor',
        'title',
        'price',
        'quantity',
        'variant_title'
    ]
        
    for line_items in order['line_items']:
        sale = {}

        for k in selected_attributes:
            if k == 'name':
                sale['order_' + k] = order[k]
            else:
                sale[k] = order[k]

        client_info = 'billing_address'

        sale = dict(sale, **order[client_info])

        for k in sales_info:
            sale[k] = line_items[k]

        sales.append(sale)
    
    return sales


def get_sales_by_date_range(sales, min_date, max_date):
    filtered_sales = []
    min_date = datetime.strptime(min_date, "%Y-%m-%d")
    max_date = datetime.strptime(max_date, "%Y-%m-%d")

    for sale in sales:
        updated_date_str = sale['updated_at'][:-6]
        updated_date = datetime.strptime(updated_date_str, "%Y-%m-%dT%H:%M:%S")
        if min_date <= updated_date and updated_date < max_date:
            filtered_sales.append(sale)
            
    return filtered_sales


def get_agg_sales(sales):
    df = pd.DataFrame()
    for sale in sales:
        sale_ = {k: [v] for k, v in sale.items()}
        df = pd.concat([df, pd.DataFrame(sale_)])

    df['price'] = df['price'].astype(float)

    sum_sales = round(df['price'].sum(), 2)

    dates = pd.DatetimeIndex([d[:-15] for d in df['updated_at']])

    df_ = pd.DataFrame({
        "date": dates,
        "price": df['price']
    })
    df_.set_index('date', inplace=True)

    df_agg = df_.groupby(pd.Grouper(freq="M")).sum().reset_index()
    df_agg['price'] = df_agg['price'].round(2)

    chart_data = df_agg.T.to_dict()
    
    return {
        "sum_sales": sum_sales,
        "chart_data": chart_data
    }
