import hmac
import json
import ssl
import time
import requests
import hashlib

from aiohttp import TCPConnector

import utils as util
import asyncio
import aiohttp
import certifi
"""
This file consists of all shopee api functions except for token generations
"""
def get_order_list(access_token,month, partner_id, partner_key, shop_id, dates):
    """
    Returns a list of all order_sn for a given month and shop
    access_token: Access_token for the shop
    month: The month you want orders from
    partner_id: The accounts partner_id
    partner_key: The secret partner_key
    shop_id: The id of the shop
    dates: The date splits for each month, since shopee only allows 15 days timespans at a time. Each month is split
    into 3 different splits, except february which has 2
    [31/30, 29], [28,15] [14,1]
    """

    timestamp = int(time.time())
    host = "https://partner.shopeemobile.com"
    path = "/api/v2/order/get_order_list"

    order_list = []

    page_size = 100 #How many orders per page
    time_range_field = "create_time"

    tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timestamp, access_token, shop_id)
    base_string = tmp_base_string.encode()
    sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
    for date in dates: #Loops through all date splits and transforms them to timestamps
        date_from, date_to = util.get_dates(date[0], date[1], month)

        time_from = util.date_to_timestamp(date_from)
        time_to = util.date_to_timestamp(date_to)
        cursor = 0
        more = True #If there is more than 100 orders we need to call several times
        while more:
            url = host + path + "?access_token=%s"  % access_token\
                            +  "&cursor=%s" % cursor\
                            + "&page_size=%s&partner_id=%s"  %(page_size,partner_id) \
                            + "&response_optional_fields=order_status" \
                            + "&shop_id=%s" % shop_id\
                            + "&sign=%s" %sign\
                            + "&time_from=%s" % time_from \
                            + "&time_range_field=%s" % time_range_field \
                            + "&time_to=%s" % time_to \
                            + "&timestamp=%s" % timestamp
            payload = {}
            headers = {"Content-Type" : "application/json"}
            response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)
            content = response.content
            data = json.loads(content)
            #print(data)
            more = data['response']['more']

            orders = [order['order_sn'] for order in data['response']['order_list']]  #Gets all the order_sns and saves in a list
            for order in orders: #IS THIS EVEN NEEDED?
                order_list.append(order)
            if more:
                print("More than 100 orders found in that timespan!!")
                print("You are killing it! <3")
                cursor += 100
    return order_list

def get_shop_ids(partner_id, main_access_token, merchant_id, partner_key): #Gets the shop_ids from a merchant
    """
    Gets all the shop_ids from shopee
    partner_id: The partner_id for the account
    main_access_token: Access token for account
    merchant_id: The merchant id for the account
    partner_key: The secret api key
    """


    host = "https://partner.shopeemobile.com"
    path = "/api/v2/merchant/get_shop_list_by_merchant"
    page_no = 1
    page_size = 100
    timestamp = int(time.time())
    tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timestamp, main_access_token, merchant_id)
    base_string = tmp_base_string.encode()
    sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()

    url = host + path + "?access_token=%s" % main_access_token \
          + "&merchant_id=%s" % merchant_id \
          + "&page_no=%s" % page_no \
          + "&page_size=%s" % page_size \
          + "&partner_id=%s" % partner_id \
          + "&sign=%s" % sign \
          + "&timestamp=%s" % timestamp

    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers, allow_redirects=False)
    content = response.content
    data = json.loads(content)
    #print(data)
    shop_ids = [shop_id['shop_id'] for shop_id in data['shop_list']]  #Specifically gets the shop_ids out from the json and puts them into a list
    return shop_ids

def get_order_detail(access_token,partner_id, partner_key, shop_id, order_string):
    """
    Gets details for each order, like amount paid, status
    access_token: Access_token for shop
    partner_id: partner_id for the account
    partner_key: Secret api key
    shop_id: The shop id
    order_string: This specific api calls for a string of order_sn separated by ','. Created outside this function
    """
    host = "https://partner.shopeemobile.com"
    path = "/api/v2/order/get_order_detail"

    timestamp = int(time.time())
    tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timestamp, access_token, shop_id)
    base_string = tmp_base_string.encode()
    sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()


    url = host + path + "?access_token=%s" % access_token \
              + "&order_sn_list=%s" % order_string \
              + "&partner_id=%s" % partner_id \
              + "&response_optional_fields=total_amount" \
              + "&shop_id=%s" % shop_id \
              + "&sign=%s" % sign \
              + "&timestamp=%s" % timestamp
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers, allow_redirects=False)
    content = response.content
    data = json.loads(content)
    #print(data)
    return data

def get_global_item_id(account, main_access_token, item_id_list, shop_id, timestamp):
    """
    Gets the global item id from an item_id+shop_id
    """
    host = "https://partner.shopeemobile.com"
    path = "/api/v2/global_product/get_global_item_id"
    #timestamp = int(time.time())
    tmp_base_string = "%s%s%s%s%s" % (account.get_partner_id(),
                                      path,
                                      timestamp,
                                      main_access_token,
                                      account.get_merchant_id())
    base_string = tmp_base_string.encode()
    sign = hmac.new(account.get_partner_key(), base_string, hashlib.sha256).hexdigest()

    url = host + path
    request_params = {
        "partner_id": int(account.get_partner_id()),
        "shop_id": int(shop_id),
        "timestamp": timestamp,
        "access_token": main_access_token,
        "item_id_list": item_id_list,
        "sign": sign,
        "merchant_id": int(account.get_merchant_id())
    }

    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers, params=request_params, allow_redirects=False)
    content = response.content
    data = json.loads(content)
    #print(data)
    global_item_id_list = [item['global_item_id'] for item in data['response']['item_id_map']]
    return global_item_id_list

def get_global_item_info(account, main_access_token, global_item_id_list, timestamp):
    """
    Gets global information for a list of global_item_ids.
    Not currently used
    """
    host = "https://partner.shopeemobile.com"
    path = "/api/v2/global_product/get_global_item_info"
    #timestamp = int(time.time())
    tmp_base_string = "%s%s%s%s%s" % (account.get_partner_id(), path, timestamp, main_access_token, account.get_merchant_id())
    base_string = tmp_base_string.encode()
    sign = hmac.new(account.get_partner_key(), base_string, hashlib.sha256).hexdigest()

    url = host + path
    request_params = {
        "partner_id": int(account.get_partner_id()),
        "timestamp": timestamp,
        "access_token": main_access_token,
        "global_item_id_list": global_item_id_list,
        "sign": sign,
        "merchant_id": int(account.get_merchant_id())
    }
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers, params=request_params, allow_redirects=False)
    content = response.content
    data = json.loads(content)
    #print(data)

    return data

def get_global_item_list(account, access_token):
    """
    Gets global_item_ids for all items for the account
    """
    host = "https://partner.shopeemobile.com"
    path = "/api/v2/global_product/get_global_item_list"

    timestamp = int(time.time())
    tmp_base_string = "%s%s%s%s%s" % (account.get_partner_id(), path, timestamp, access_token, account.get_merchant_id())
    base_string = tmp_base_string.encode()
    sign = hmac.new(account.get_partner_key(), base_string, hashlib.sha256).hexdigest()

    offset = ""
    page_size = 50
    has_next_page = True
    global_item_id_list = []
    while has_next_page:
        url = host + path + "?access_token=%s" % access_token \
                + "&partner_id=%s" % account.get_partner_id() \
                + "&sign=%s" % sign \
                + "&timestamp=%s" % timestamp \
                + "&merchant_id=%s" % account.get_merchant_id() \
                + "&offset=%s" % offset \
                + "&page_size=%s" % page_size
        headers = {"Content-Type": "application/json"}
        response = requests.get(url, headers=headers, allow_redirects=False)
        content = response.content
        data = json.loads(content)

        has_next_page = data['response']['has_next_page']
        offset = data['response']['offset']
        for list_of_ids in data['response']['global_item_list']:
            global_item_id_list.append(list_of_ids['global_item_id'])
    return global_item_id_list

def get_escrow_detail(partner_id, access_token, partner_key, shop_id, order_sn):
    """
    Gets escrow detail for a specific order
    """
    host = "https://partner.shopeemobile.com"
    path = "/api/v2/payment/get_escrow_detail"

    timestamp = int(time.time())
    tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timestamp, access_token, shop_id)
    base_string = tmp_base_string.encode()
    sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()

    url = host + path + "?access_token=%s" % access_token \
          + "&shop_id=%s" % shop_id \
          + "&partner_id=%s" % partner_id \
          + "&sign=%s" % sign \
          + "&timestamp=%s" % timestamp\
          + "&order_sn=%s" % order_sn

    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers, allow_redirects=False)
    content = response.content
    data = json.loads(content)
    #print(data)
    escrow_amount = data['response']['order_income']['escrow_amount']
    return escrow_amount

def get_escrow_detail_batch(partner_id, access_token, partner_key, shop_id, order_sn_list):
    """Gets escrow detail for a batch of orders"""

    host = "https://partner.shopeemobile.com"
    path = "/api/v2/payment/get_escrow_detail_batch"
    timestamp = int(time.time())
    tmp_base_string = "%s%s%s%s%s" % (partner_id, path, timestamp, access_token, shop_id)
    base_string = tmp_base_string.encode()
    sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
    url = host + path

    query_params = {
        "partner_id": partner_id,
        "shop_id": shop_id,
        "timestamp": timestamp,
        "sign": sign,
        "access_token": access_token
    }

    payload = {
        "order_sn_list": order_sn_list
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, params= query_params, json= payload, allow_redirects=False)
    content = response.content
    data = json.loads(content)
    #print(data)

    return data


def get_global_model_list(account, main_access_token, global_item_id):
    """
    This like get_global_item_info but on the model level
    For a given global_item_id it returns a list of models for that item
    """

    host = "https://partner.shopeemobile.com"
    path = "/api/v2/global_product/get_global_model_list"
    url = host + path
    timestamp = int(time.time())
    tmp_base_string = "%s%s%s%s%s" % (account.get_partner_id(), path, timestamp, main_access_token, account.get_merchant_id())
    base_string = tmp_base_string.encode()
    sign = hmac.new(account.get_partner_key(), base_string, hashlib.sha256).hexdigest()

    request_params = {
        "partner_id": int(account.get_partner_id()),
        "timestamp": timestamp,
        "access_token": main_access_token,
        "global_item_id": global_item_id,
        "sign": sign,
        "merchant_id": int(account.get_merchant_id())
    }

    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers, params=request_params, allow_redirects=False)
    content = response.content
    data = json.loads(content)
    #print(data)
    return data

async def process_get_global_model_list(session, account, main_access_token, global_item_id):
    """
     This is like get_global_model_list but made to work with asyncio library to call several times
     For a given global_item_id it returns a list of models for that item
     """

    try:
        #print(f"Started api request of index: {index}.")

        host = "https://partner.shopeemobile.com"
        path = "/api/v2/global_product/get_global_model_list"

        timestamp = int(time.time())
        tmp_base_string = "%s%s%s%s%s" % (
        account.get_partner_id(), path, timestamp, main_access_token, account.get_merchant_id())
        base_string = tmp_base_string.encode()
        sign = hmac.new(account.get_partner_key(), base_string, hashlib.sha256).hexdigest()

        url = host + path + "?partner_id=%s" % account.get_partner_id() \
                        + "&timestamp=%s" % timestamp \
                        + "&access_token=%s" % main_access_token \
                        + "&global_item_id=%s" % global_item_id \
                        + "&sign=%s" % sign \
                        + "&merchant_id=%s" % account.get_merchant_id()

        async with await session.get(url) as response:
            data = await response.json()
            #print(f"Finished api request of index: {index}.")
            # print(data)
            return data
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

async def run_concurrent_get_global_model_list_requests(concurrent_requests, account, main_access_token, global_item_id_list):
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        async with aiohttp.ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
            global_model_json_list = [
                process_get_global_model_list(session, account, main_access_token, global_item_id_list[index])
                for index in range(min(concurrent_requests, len(global_item_id_list)))
            ]
            return await asyncio.gather(*global_model_json_list, return_exceptions=True)