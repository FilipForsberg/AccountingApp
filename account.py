class Account:
    """
    The account class
    code: This is the last authentication code, only used when a new authentication is needed
    main_account_id: The account id in shopee
    partner_id: The partner id for the account
    merchant_id: The merchant id for the account
    partner_key = The secret api key, hashed version is stored in .txt file

    """
    def __init__(self, partner_key):
        self.code = "6773634b4f7a4647585148454f6c4763"
        self.main_account_id = 1104708
        self.partner_id = 2009434
        self.merchant_id = 1309479
        self.tmp_partner_key = str(partner_key)

    def set_code(self, new_code):
        self.code = new_code
        return self.code

    def get_code(self):
        return self.code

    def get_main_account_id(self):
        return self.main_account_id

    def get_partner_id(self):
        return self.partner_id

    def get_merchant_id(self):
        return self.merchant_id

    def get_partner_key(self):
        return self.tmp_partner_key.encode()