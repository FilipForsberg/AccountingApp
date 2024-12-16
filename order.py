import datetime

"""
The order class represents each order. Each order has some attributes and consists of items
date: Date when it was ordered, given as a timestamp and remade to a date
status: Status of the order {cancelled, completed, etc}
order_id: The identifier for the order
currency: Denotes which currency the order was made in
amount: Amount paid by the costumer
items: Item objects for each item in the order
order_escrow: The expected income for the order (DOES NOT INCLUDE THE COST OF EACH ITEM)
shop: Which shop the order was made in, given as an shop id
"""
class Order:
    def __init__(self, date, status, order_id, currency, amount, items, order_escrow):
        self.date = datetime.date.fromtimestamp(date)
        self.order_id = order_id
        self.currency = currency
        self.amount = amount
        self.items = items
        self.escrow = order_escrow
        self.status = status

    def get_date(self):
        return self.date

    def get_order_id(self):
        return self.order_id

    def get_items(self):
        return self.items

    def get_currency(self):
        return self.currency

    def get_order_status(self):
        return self.status

    def get_order_escrow(self):
        return self.escrow

    def get_order_cost(self): #Order income is the escrow - original cost of each item
        cost_of_items = 0
        for item in self.items:
            if item.get_purchase_price() == 0:
                return "ERROR"
            cost_of_items += (item.get_purchase_price() * item.get_item_quantity())
        return cost_of_items

    def get_total_items(self):
        total_items = 0
        for item in self.items:
            total_items += item.get_item_quantity()
        return total_items

    def update_item_prices(self, list_of_model_prices):
        for item in self.get_items():
            price = self.find_model_price(list_of_model_prices, item.get_item_model().get_model_sku())
            if not price: #If it cant find the price, means that the model_sku and global_model_sku are not the same
                print("Error: Model_Sku was not found and therefore price was not changed")
                print("The order_sn is:", self.get_order_id())
            else:
                item.set_purchase_price(price)

    def print_order_info(self):
        print("Order id: %s and was ordered on: %s" %(self.order_id,self.date))
        print("Order status is: ", self.status)
        print("Order value was: %s and expected income is: %s (All given in %s)" %(self.amount ,self.escrow ,self.currency))
        print("The items ordered were:")
        print("---------------------------------------------------------------------")
        for item in self.items:
            item.print_item_info()
        print("---------------------------------------------------------------------")
        return 0

    def find_model_price(self,my_2d_list,find_this_element):  # This function finds the first instance of an element in a 2d list and returns the 2nd element
        for item in my_2d_list:
            model_sku = item[0]
            price = item[1]
            if find_this_element == model_sku:
                return price
        return False
