import sys
import utils as util
import shopee_api as api
import item as it
import order as order_object
import model as model
import time as time
import asyncio

def get_orders_all(ac, shops, main_access_token, month):
    """
    The function initiates the creation of all orders, for all shops in a given month, returns the order objects
    and item_id_list (To fetch prices later)
    """
    all_orders_objects = []
    item_id_list = []
    dates = util.get_date_splits(month)
    time_start = time.time()
    for shop in shops:
        new_orders,new_item_ids = get_orders_shop(shop, ac, month, dates, main_access_token)
        all_orders_objects += new_orders
        item_id_list.append(new_item_ids)
    print("____________________________________")
    print("Total numbers of orders created:", len(all_orders_objects))
    time_end = time.time()
    print("Time to create orders:", time_end-time_start)
    return all_orders_objects, item_id_list


def get_orders_shop(shop, ac, month, dates, main_access_token):
    """
    Gets order_list for specific shop and then calls on createOrders to create order objects
    """

    print("____________________________________")
    print("Now creating orders for shop id:", shop[0])
    shop_id = shop[0]
    shop_access_token = shop[1]
    order_sn_list = api.get_order_list(shop_access_token, month, ac.get_partner_id(), ac.get_partner_key(), shop_id, dates)
    list_of_order_objects, item_id_list = create_orders(order_sn_list, ac, shop_access_token, shop_id)
    print("Created this many orders:", len(list_of_order_objects))

    return list_of_order_objects, (item_id_list, shop_id)


def create_orders(order_list,ac, shop_access_token, shop_id):
    """
    Creates the order objects from the order_list
    """
    item_id_list = []
    order_objects_list = []
    for n in range(0, len(order_list), 49): #Shopee only allows 49 at a time, and api requires the order_sn input as a str, where order_sn is separated by ','
        order_string = ""
        if len(order_list) == 1:
            #Don't want to add a ',' if there's only 1 order. Either 1 in total or as a left over from mod49
            order_string = order_list[0]
        else:
            for order in order_list[n:n+49]:
                order_string += order +","
        #Get the escrow and order detail (49 orders at a time)
        escrow_json_data = api.get_escrow_detail_batch(ac.get_partner_id(), shop_access_token, ac.get_partner_key(),shop_id, order_list[n:n + 49])
        orders_json_data = api.get_order_detail(shop_access_token,ac.get_partner_id(), ac.get_partner_key(), shop_id, order_string)
        try:
            orders = [order for order in orders_json_data['response']['order_list']]
            escrow_details = [escrow['escrow_detail'] for escrow in escrow_json_data['response']]
            # Creating order_object and adding to the list of order_objects
            new_orders, new_item_ids = create_order_objects(orders, escrow_details, item_id_list)
            order_objects_list += new_orders
            return order_objects_list, item_id_list
        except Exception as e:
            print(f"ERROR: {e}")
            print("Exiting the program")
            sys.exit()

def fetch_global_ids(ac, main_access_token, item_id_list, shop_id):
    """
    This function takes a list of item_ids for a shop and fetches their global_item_ids. Only returns the unique ones to minimize the amount of api calls needed.
    """
    print("Now fetching global item ids for the unique %s items in shop: %s"%(len(item_id_list),shop_id))
    unique_item_id_list = []
    global_item_id_list = []
    for item in item_id_list:
        if item not in unique_item_id_list:
            unique_item_id_list.append(item)
    timestamp = int(time.time())
    for n in range(0, len(unique_item_id_list), 20):
        global_item_id_list += api.get_global_item_id(ac, main_access_token, unique_item_id_list[n:n + 20], shop_id,timestamp)

    return global_item_id_list

def fetch_and_update_item_price(ac,orders, global_item_id_list, main_access_token):
    """
    Fetching the model original global_model_sku and original price , then compares to each order (Global_model_sku should be the same model_sku is the same)
    Updates the item price for each item in each order
    """

    global_model_list = []
    for n in range(0, len(global_item_id_list), 10):
        global_model_json_list = asyncio.run(api.run_concurrent_get_global_model_list_requests(10, ac, main_access_token,global_item_id_list[n:n+10]))
        global_model_list += parse_global_model_list_json(global_model_json_list)

    for order in orders:
        order.update_item_prices(global_model_list)
    return True

def parse_global_model_list_json(data):
    global_model_list = []
    for model_list in data:
        for global_model in model_list['response']['global_model']:
            try:
                global_model_sku = global_model['global_model_sku']
                original_price = global_model['price_info']['original_price']
                global_model_list.append((global_model_sku, original_price))
            except Exception as e:
                print(f"Error: {e}")
                print("Happened while trying to parse:", global_model)
                print("Exiting the program")
                sys.exit()
    return global_model_list


def create_order_objects(order_batch, escrow_details_list, item_id_list):
    order_objects = []

    escrow_sns = [escrow['order_sn'] for escrow in escrow_details_list] #Finds the order_sn in the escrow_details
    for order in order_batch:  # Getting the wanted information from the orders_json_data
        items = []
        order_currency = order['currency']
        order_total_amount = order['total_amount']
        order_time = order['create_time']
        order_sn = order['order_sn']
        order_status = order['order_status']

        #Find the correct escrow_detail for current order
        order_escrow_index = escrow_sns.index(order_sn)
        escrow_detail = escrow_details_list[order_escrow_index]
        order_escrow = escrow_detail['order_income']['escrow_amount']
        for item in escrow_detail['order_income']['items']:
            item_id = item['item_id']
            item_name = item['item_name']
            item_sku = item['item_sku']
            item_quantity = item['quantity_purchased']

            model_id = item['model_id']
            model_name = item['model_name']
            model_sku = item['model_sku']
            if item_id not in item_id_list:
                item_id_list.append(item_id)
            # Creating model object -> item object -> order object
            new_model = model.Model(model_id, model_name, model_sku)
            new_item = it.Item(item_id, item_name, item_sku, new_model, item_quantity)
            items.append(new_item)
        order_objects.append(order_object.Order(order_time, order_status, order_sn, order_currency, order_total_amount, items, order_escrow))
    return order_objects, item_id_list