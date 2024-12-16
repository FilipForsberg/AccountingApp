"""
The class model represents the different kinds of models for each item
model_id: The model_id in shopee's database
model_name: The specific name of the model
model_sku: The sku identifies the model in shopee database. Model_sku SHOULD be the same as global_model_sku
"""

class Model:
    def __init__(self, model_id, model_name, model_sku):
        self.model_id = model_id
        self.model_name = model_name
        self.model_sku = model_sku

    def get_model_id(self):
        return self.model_id

    def get_model_name(self):
        return self.model_name

    def get_model_sku(self):
        return self.model_sku