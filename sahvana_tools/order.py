def get_agg_orders(vendor):
    client = MongoClient(os.environ['DATABASE_URL'])
    db = client["sahvana-dev"]
    collection = db["orders"]

    query = {'Vendor': vendor}
    results = list(collection.find(query))

    sales, dates = [], []
    for result in results :
        dates.append(result['Paid at'])
        sales.append(result['Subtotal'])

    df = pd.DataFrame({
        'Paid at': dates,
        'Subtotal': sales
    })
    df.sort_values(by='Paid at', inplace=True)
    df.set_index('Paid at', inplace=True)

    g = df.groupby(pd.Grouper(freq="M"))
    df = g.sum().reset_index()

    data = []
    for i in range(len(df)):
        date = df.iloc[i]['Paid at']
        date = date.strftime("%d-%m-%Y")
        sales = df.iloc[i]['Subtotal']
        data.append({'time': date, 'amount': sales})
        
    return {'data': data}

def get_sum_sales(vendor):
    client = MongoClient(os.environ['DATABASE_URL'])
    db = client["sahvana-dev"]
    collection = db["orders"]

    query = {'Vendor': vendor}
    results = list(collection.find(query))

    total_sales = 0
    for result in results:
        total_sales += result['Subtotal']

    return {'total_sales': total_sales}

def get_orders(vendor):
    client = MongoClient(os.environ['DATABASE_URL'])
    db = client["sahvana-dev"]
    collection = db["orders"]

    query = {'Vendor': vendor}
    results = list(collection.find(query))
    last_results = results[-5:]
    last_results = last_results[::-1]

    data = []
    c = 0
    for result in last_results:
        date = result['Paid at']
        date = date.strftime("%d-%m-%Y")
        name = result['Billing Name']
        shipTo = result['Shipping City'] + ',' + result['Shipping Province']
        product = result['Lineitem name']
        amount = result['Subtotal']
        data.append({
            'id': c,
            'date': date,
            'name': name,
            'shipTo': shipTo,
            'product': product,
            'amount': amount
        })
        c += 1

    return {'data': data}