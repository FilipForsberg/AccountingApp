"""
The class item represents the items in each order. Each item has some qualities and a model
item_id: Item id in the shopee database for one shop. Used to get global_item_id
item_name: Name of the item
item_sku: Item identifier, same as global_item_sku
model: A model object for the item
quantity: How many of this item was purchased
purchased_for: The cost of buying the item from supplier
"""

class Item:
    def __init__(self, item_id, item_name, item_sku, model,item_quantity, ):
        self.item_id = item_id
        self.item_name = item_name
        self.item_sku = item_sku
        self.model = model
        self.quantity = item_quantity

        self.purchased_for = 0

    def get_item_id(self):
        return int(self.item_id)

    def get_item_sku(self):
        return self.item_sku

    def set_purchase_price(self, price):
        self.purchased_for = price
        return True

    def get_item_name(self):
        return self.item_name

    def get_item_quantity(self):
        return self.quantity

    def get_item_model(self):
        return self.model

    def get_purchase_price(self):
        return self.purchased_for

    def print_item_info(self):
        print("Item name: " , self.item_name)
        print("Has the item ID: ", self.item_id)
        print("The specific model ID: ", self.model.get_model_id())
        print("Item sku: ", self.item_sku, "; and model sku: ", self.model.get_model_sku())
        print("They bought %s of this item" % self.quantity)
        return 0
