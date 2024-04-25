import json
import requests
import pytz
import os
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

def lambda_handler(event, context):
    
    # Get the current timestamp in UTC
    central = pytz.timezone('America/Chicago')
    timestamp_format = "%Y-%m-%dT%H:%M:%SZ"
    current_timestamp = datetime.now(pytz.utc)
    
    # # Set up your Shopify store details and authentication
    SHOP_URL = "organicbakeryaustin.com"
    ACCESS_TOKEN = os.getenv('SHOPIFY_ADMIN_API_PROD_ACCESS_TOKEN', 'DefaultAccessToken')
    VERSION = "2024-04"  # Adjust based on the latest API version
    
    base_endpoint = f"https://{SHOP_URL}/admin/api/{VERSION}"
    orders_endpoint = f"{base_endpoint}/orders.json?status=open"
    
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": ACCESS_TOKEN
    }
    
    # # Make the HTTP GET request
    response = requests.get(orders_endpoint, headers=headers)
    
    # Result Set
    result_set = []

    def fetch_metafields(order, base_endpoint, headers):
        metafields_url = f"{base_endpoint}/orders/{order['id']}/metafields.json"
        response = requests.get(metafields_url, headers=headers)
        if response.status_code == 200:
            metafields = response.json().get('metafields', [])
            time.sleep(0.5) # We have limits to get 2 api in a second from Shopify
            return order, metafields
        else:
            print(f"Failed to fetch metafields: {response.status_code} {response.text}")
            return order, None
    
    # Check if the request was successful
    if response.status_code == 200:

        orders = response.json().get('orders', [])

        with ThreadPoolExecutor(max_workers=2) as executor:

            future_to_order = {executor.submit(fetch_metafields, order, base_endpoint, headers): order for order in orders}

            for future in as_completed(future_to_order):
                order, metafields = future.result()

                if metafields:
                    pickup_datetime, order_type = None, None
                    for metafield in metafields:
                        if metafield["key"] == "pickup_date":
                            pickup_datetime = metafield["value"]
                        elif metafield["key"] == "draft_type":
                            order_type = metafield["value"]

                    current_timestamp = datetime.now(pytz.utc)
                    if not pickup_datetime or current_timestamp <= datetime.strptime(pickup_datetime, timestamp_format).replace(tzinfo=pytz.utc):
                        central_pickup_datetime = datetime.strptime(pickup_datetime, timestamp_format).replace(tzinfo=pytz.utc).astimezone(central) if pickup_datetime else None
                        central_pickup_datetime_str = datetime.strftime(central_pickup_datetime, timestamp_format) if pickup_datetime else "0"

                        result_set.append({
                            "order_id": order['name'],
                            "first_name": order["customer"]["first_name"],
                            "status": order['financial_status'],
                            "order_type": order_type,
                            "pickup_datetime": central_pickup_datetime_str
                        })

        result_set.sort(key=lambda x: x['pickup_datetime'])

    else:
        print("Failed to fetch orders:", response.status_code, response.text)
    
    # Error handling and further processing logic here as needed
    
    return {
        'statusCode': 200,
        'body': json.dumps(result_set)
    }
