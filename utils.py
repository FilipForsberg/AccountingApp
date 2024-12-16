import datetime
import time
import hashlib
import numpy as np
import pandas as pd
"""
This file consists of util functions. These are used throughout the code
"""
months = { #Dictionary to transform months to int
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}
reverse_months = { #Dictionary to transform ints to months
    1: "jan",
    2: "feb",
    3: "mar",
    4: "apr",
    5: "may",
    6: "jun",
    7: "jul",
    8: "aug",
    9: "sep",
    10: "oct",
    11: "nov",
    12: "dec"
}

currency = { #Dictionary for the different currencies. You divide the amount in the given currency with the value to get it in CNY
    'TWD': 4.5,
    'THB': 5.405,
    'PHP': 8.33,
    'SGD': 0.187,
    'VND': 3600
}

def date_to_timestamp(datetime_object): #Converts a datetime object into a timestamp. Given in chinese mainland time
    month = datetime_object.month
    new_dt = datetime_object.timetuple()
    dt_time = time.mktime(new_dt)

    #Subtraction by (60*60*8) seconds is because chinese time is utc + 8
    if datetime_object.day == 1 or datetime_object.day == 31:
        dt_time = dt_time - (60*60*8)
    elif datetime_object.day == 28 and month == 2:
        dt_time = dt_time - (60 * 60 * 8)
    elif datetime_object.day == 30 and month in [4, 6, 9, 11]:
        dt_time = dt_time - (60 * 60 * 8)


    return int(dt_time)


def get_dates(first_day_digit, second_day_digit, month_digit): #Creates the dates for first day of the month and last day of the month
    current_date = datetime.datetime.today()
    if month_digit > current_date.month:
        #We are in last year
        from_date = current_date.replace(current_date.year - 1, month_digit, first_day_digit, 0, 0, 0, 0)
        to_date = current_date.replace(current_date.year - 1, month_digit, second_day_digit, 23, 59, 59, 0)
    else:
        from_date = current_date.replace(current_date.year, month_digit, first_day_digit, 0, 0, 0, 0)
        to_date = current_date.replace(current_date.year, month_digit, second_day_digit, 23, 59, 59, 0)
    return from_date,to_date

def get_date_splits(month_digit): #Divides the month in 2 or 3 date splits. Used since Shopee only allows 15 day timespans
    long_months = [1, 3, 5, 7, 8, 10, 12]
    short_months = [4, 6, 9, 11]
    if month_digit in long_months:
        last_day = 31
    elif month_digit in short_months:
        last_day = 30
    else:
        last_day = 28

    if last_day > 28:
        dates = [[29, last_day], [15, 28], [1, 14]]
    else:
        dates = [[15, 28], [1, 14]]
    return dates

def update_shop_tokens_list(refresh_token_list): #Updates the txt file with shop tokens, input is a list of refresh_tokens
    open('shopTokens.txt', 'w').close()
    file = open('shopTokens.txt', 'a')
    for token in refresh_token_list:
        file.write(token + "\n")
    return 0

def get_month_input(): #Meny and input handling for month. Converts a str to an int representation.
    while True:
        print("{ jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec }")
        month = input("Which month do you want to calculate: ")
        try:
            month = months[month]
            break
        except:
            print("Incorrect input, try again")
    return month

def get_shop_id_input(shop_ids): #Meny and input handling for shop_id
    while True:
        print("These are the shop ids: ", shop_ids)
        shop = input("Input the shop id for the shop: ")
        if shop in shop_ids:
            break
        else:
            print("Incorrect input, try again")
    return int(shop)

def check_partner_key_hash(): #Checks the input of partner_key to saved hashed version
    f = open("hashed_key.txt")
    hashed_key = f.read()
    f.close()
    while True:
        partner_key = input("Whats your partner key?: ")
        input_to_compare = hashlib.sha512(partner_key.encode())
        input_to_compare = input_to_compare.hexdigest()

        if input_to_compare == hashed_key:
            print("Correct key!")
            return partner_key
        else:
            print("Wrong key, try again!")

def meny(): #Meny and input handling for main meny
    print("\n******************************************")
    print("1: Calculate for all shops ")
    print("2: Do something different?")
    print("3: End program")
    print("****************************************** \n")
    option = input("Pick an option: ")
    return option

def make_xlsx_file(list_of_order_objects, month_digit): #Creates the Excel file
    csv_rows = []
    csv_columns= ["Order Date" , "Order sn", "Amount of Items", "Status", "Currency", "Escrow" , "Cost of Items"] #The headers of the Excel file
    for order in list_of_order_objects:
        #All the values we want represented
        order_date = order.get_date()
        order_sn = order.get_order_id()
        order_total_items = order.get_total_items()
        order_status = order.get_order_status()
        order_currency = order.get_currency()
        order_escrow = order.get_order_escrow()
        order_cost = order.get_order_cost()
        csv_rows.append((order_date, order_sn, order_total_items, order_status, order_currency, order_escrow, order_cost))
    sheet = pd.DataFrame(np.array(csv_rows), columns = csv_columns)

    #This logic is just for naming of file
    current_date = datetime.datetime.today()
    if month_digit > current_date.month:
        year = current_date.year-1
    else:
        year = current_date.year
    file_path = "order_excels/" + "orders" + "-" + str(year) +"-" + reverse_months[month_digit] + ".xlsx"
    return sheet.style.apply(highlight_error_cost, subset=['Cost of Items']).to_excel(excel_writer=file_path, index = False)  #Applies the highlight_error_cost style and creates Excel file


def highlight_error_cost(x): #Highlights the values in the panda series x red IF they have the value "ERROR"
    is_error = x == "ERROR"
    return ['background-color: red' if x else "" for x in is_error]
