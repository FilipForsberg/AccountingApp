import generate_tokens as token
import utils as util
import account as account
import shopee_api as api
import orderCreation as oC
import time as time

if __name__ == '__main__':
    partner_key = util.check_partner_key_hash()  #Checks if the given partner key matches the saved hashed one
    token_start_time = int(time.time())
    total_start_time = int(time.time())
    ac = account.Account(partner_key) #creates an account with the given partner key

    main_access_token, main_new_refresh_token, auth = token.check_account_token(ac)  #Checks if refresh token exists for account, otherwise initiates an auth
    shop_ids = api.get_shop_ids(ac.get_partner_id(), main_access_token, ac.get_merchant_id(), ac.get_partner_key()) #Gets all shop ids from shopee
    shop_account_id_tokens = token.get_shop_tokens(ac, shop_ids, main_new_refresh_token, auth) #Checks if refresh tokens exists for shops and gets access_tokens + saves new refresh tokens
    token_end_time = int(time.time())
    print("Time to get tokens:", token_end_time-token_start_time)
    run = True
    while run:

        option = util.meny()  #Prints the meny

        if option == '1':
            #print(shop_account_tokens)
            month = util.get_month_input()
            orders, shop_item_id_list = oC.get_orders_all(ac, shop_account_id_tokens, main_access_token, month) #Gets the orders for all shops and also shop_item_id_list which is used to get the original price
            model_item_prices = []
            fetch_start_time = int(time.time())
            total_global_item_id_list = []
            for element in shop_item_id_list: #Shop_item_id_list consists of lists of (item_id_list, shop_ids)
                item_id_list = element[0]
                shop_id = element[1]
                partial_global_id_list = oC.fetch_global_ids(ac, main_access_token, item_id_list, shop_id) #Get the global ids for each item
                for iD in partial_global_id_list: #Make sure to only save the unique ids
                    if iD not in total_global_item_id_list:
                        total_global_item_id_list.append(iD)
            fetch_end_time = int(time.time())
            print("Fetching global_ids took:", fetch_end_time-fetch_start_time)

            update_price_start = int(time.time())

            print("Fetching and updating prices")

            oC.fetch_and_update_item_price(ac, orders, total_global_item_id_list, main_access_token)  #Get the original price for each item and change every item price variable in each order
            update_price_end = int(time.time())

            print("Fetching and Updating price took:", update_price_end-update_price_start)

            total_end_time = int(time.time())

            print("Total time to calculate:", total_end_time-total_start_time)

            sheet = util.make_xlsx_file(orders,month)
        elif option == '2':
            #TODO DO WE WANT SOME DIFFERENT FUNCTION HERE
            print("TODO")
        elif option == '3':
            print("Bye bye")
            run = False
            break
        else:
            print("Incorrect option try again \n")
